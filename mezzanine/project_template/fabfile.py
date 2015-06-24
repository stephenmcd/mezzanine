from __future__ import print_function, unicode_literals
from future.builtins import open

import os
import re
import sys
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from getpass import getpass, getuser
from glob import glob
from importlib import import_module
from posixpath import join

from mezzanine.utils.conf import real_project_name

from fabric.api import abort, env, execute, cd, prefix, sudo as _sudo, \
    run as _run, hide, task, local
from fabric.context_managers import settings as fab_settings
from fabric.contrib.console import confirm
from fabric.contrib.files import exists, upload_template
from fabric.contrib.project import rsync_project
from fabric.colors import yellow, green, blue, red
from fabric.decorators import hosts


################
# Config setup #
################

env.proj_app = real_project_name("{{ project_name }}")

conf = {}
if sys.argv[0].split(os.sep)[-1] in ("fab", "fab-script.py"):
    # Ensure we import settings from the current dir
    try:
        fabric_dict = __import__("settings", globals(), locals(), [], 0).FABRIC
        try:
            conf = fabric_dict['DEFAULT']
        except KeyError:
            print('Your FABRIC dictionary uses the old, deprecated '
                  'format, continuing.')
            conf = fabric_dict
        try:
            conf["HOSTS"][0]
        except (KeyError, ValueError):
            raise ImportError
    except (ImportError, AttributeError):
        abort('Aborting, no hosts defined.')


def conf_lookup(default_conf, conf_overrides, key, fallback=None):
    """
    Returns the value of the specified key in the passed FABENV,
    falling back to defaults
    """
    return conf_overrides.get(key, default_conf.get(key, fallback)) or fallback

def setup_env(env_string=None):
    """
    Sets up the fabric env dict potentially with a specified sub dict from
    the setting FABRIC
    """
    conf_overrides = {}

    if env_string:
        # Override config based on a passed in key, i.e. DEV/STAGE/PROD
        try:
            conf_overrides = fabric_dict[env_string]
        except KeyError:
            abort('Specified ENV, %s, does not exist in the '
                  'FABRIC dict' % env.FABENV)

    env.db_pass = conf_lookup(conf, conf_overrides, "DB_PASS")
    env.admin_pass = conf_lookup(conf, conf_overrides, "ADMIN_PASS")
    env.user = conf_lookup(conf, conf_overrides, "SSH_USER", getuser())
    env.password = conf_lookup(conf, conf_overrides, "SSH_PASS")
    env.key_filename = conf_lookup(conf, conf_overrides, "SSH_KEY_PATH")
    env.hosts = conf_lookup(conf, conf_overrides, "HOSTS", [""])

    env.proj_name = conf_lookup(conf, conf_overrides,
                                "PROJECT_NAME", os.getcwd().split(os.sep)[-1])
    env.venv_home = conf_lookup(conf, conf_overrides,
                                "VIRTUALENV_HOME", "/home/%s" % env.user)
    env.venv_path = join(env.venv_home, env.proj_name)
    env.proj_path = "/home/%s/mezzanine/%s" % (env.user, env.proj_name)
    env.manage = "%s/bin/python %s/manage.py" % (env.venv_path, env.proj_path)
    env.domains = conf_lookup(
        conf, conf_overrides, "DOMAINS",
        [conf_lookup(conf, conf_overrides, "LIVE_HOSTNAME", env.hosts[0])])
    env.domains_nginx = " ".join(env.domains)
    env.domains_regex = "|".join(env.domains)
    env.domains_python = ", ".join(["'%s'" % s for s in env.domains])
    env.ssl_disabled = "#" if len(env.domains) > 1 else ""
    env.vcs_tools = ["git", "hg"]
    env.deploy_tool = conf_lookup(conf, conf_overrides, "DEPLOY_TOOL", "rsync")
    env.reqs_path = conf_lookup(conf, conf_overrides, "REQUIREMENTS_PATH")
    env.locale = conf.get("LOCALE", "en_US.UTF-8")
    env.num_workers = conf_lookup(conf, conf_overrides, "NUM_WORKERS",
                               "multiprocessing.cpu_count() * 2 + 1")

    env.secret_key = conf_lookup(conf, conf_overrides, "SECRET_KEY", "")
    env.nevercache_key = conf_lookup(conf, conf_overrides,
                                     "NEVERCACHE_KEY", "")

    # Remote git repos need to be "bare" and reside separated from the project
    if env.deploy_tool == "git":
        env.repo_path = "/home/%s/git/%s.git" % (env.user, env.proj_name)
    else:
        env.repo_path = env.proj_path


##################
# Template setup #
##################

# Each template gets uploaded at deploy time, only if their
# contents has changed, in which case, the reload command is
# also run.

templates = {
    "nginx": {
        "local_path": "deploy/nginx.conf.template",
        "remote_path": "/etc/nginx/sites-enabled/%(proj_name)s.conf",
        "reload_command": "service nginx restart",
    },
    "supervisor": {
        "local_path": "deploy/supervisor.conf.template",
        "remote_path": "/etc/supervisor/conf.d/%(proj_name)s.conf",
        "reload_command": "supervisorctl update gunicorn_%(proj_name)s",
    },
    "cron": {
        "local_path": "deploy/crontab.template",
        "remote_path": "/etc/cron.d/%(proj_name)s",
        "owner": "root",
        "mode": "600",
    },
    "gunicorn": {
        "local_path": "deploy/gunicorn.conf.py.template",
        "remote_path": "%(proj_path)s/gunicorn.conf.py",
    },
    "settings": {
        "local_path": "deploy/local_settings.py.template",
        "remote_path": "%(proj_path)s/%(proj_app)s/local_settings.py",
    },
}


######################################
# Context for virtualenv and project #
######################################

@contextmanager
def virtualenv():
    """
    Runs commands within the project's virtualenv.
    """
    with cd(env.venv_path):
        with prefix("source %s/bin/activate" % env.venv_path):
            yield


@contextmanager
def project():
    """
    Runs commands within the project's directory.
    """
    with virtualenv():
        with cd(env.proj_path):
            yield


@contextmanager
def update_changed_requirements():
    """
    Checks for changes in the requirements file across an update,
    and gets new requirements if changes have occurred.
    """
    reqs_path = join(env.proj_path, env.reqs_path)
    get_reqs = lambda: run("cat %s" % reqs_path, show=False)
    old_reqs = get_reqs() if env.reqs_path else ""
    yield
    if old_reqs:
        new_reqs = get_reqs()
        if old_reqs == new_reqs:
            # Unpinned requirements should always be checked.
            for req in new_reqs.split("\n"):
                if req.startswith("-e"):
                    if "@" not in req:
                        # Editable requirement without pinned commit.
                        break
                elif req.strip() and not req.startswith("#"):
                    if not set(">=<") & set(req):
                        # PyPI requirement without version.
                        break
            else:
                # All requirements are pinned.
                return
        pip("-r %s/%s" % (env.proj_path, env.reqs_path))


###########################################
# Utils and wrappers for various commands #
###########################################

def _print(output):
    print()
    print(output)
    print()


def print_command(command):
    _print(blue("$ ", bold=True) +
           yellow(command, bold=True) +
           red(" ->", bold=True))


@task
def run(command, show=True, *args, **kwargs):
    """
    Runs a shell comand on the remote server.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _run(command, *args, **kwargs)


@task
def sudo(command, show=True, *args, **kwargs):
    """
    Runs a command as sudo on the remote server.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _sudo(command, *args, **kwargs)


def log_call(func):
    @wraps(func)
    def logged(*args, **kawrgs):
        header = "-" * len(func.__name__)
        _print(green("\n".join([header, func.__name__, header]), bold=True))
        return func(*args, **kawrgs)
    return logged


def get_templates():
    """
    Returns each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected


def upload_template_and_reload(name):
    """
    Uploads a template only if it has changed, and if so, reload the
    related service.
    """
    template = get_templates()[name]
    local_path = template["local_path"]
    if not os.path.exists(local_path):
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(project_root, local_path)
    remote_path = template["remote_path"]
    reload_command = template.get("reload_command")
    owner = template.get("owner")
    mode = template.get("mode")
    remote_data = ""
    if exists(remote_path):
        with hide("stdout"):
            remote_data = sudo("cat %s" % remote_path, show=False)
    with open(local_path, "r") as f:
        local_data = f.read()
        # Escape all non-string-formatting-placeholder occurrences of '%':
        local_data = re.sub(r"%(?!\(\w+\)s)", "%%", local_data)
        if "%(db_pass)s" in local_data:
            env.db_pass = db_pass()
        local_data %= env
    clean = lambda s: s.replace("\n", "").replace("\r", "").strip()
    if clean(remote_data) == clean(local_data):
        return
    upload_template(local_path, remote_path, env, use_sudo=True, backup=False)
    if owner:
        sudo("chown %s %s" % (owner, remote_path))
    if mode:
        sudo("chmod %s %s" % (mode, remote_path))
    if reload_command:
        sudo(reload_command)


def rsync_upload():
    """
    Uploads the project with rsync excluding some files and folders.
    """
    excludes = ["*.pyc", "*.pyo", "*.db", ".DS_Store", ".coverage",
                "local_settings.py", "/static", "/.git", "/.hg"]
    local_dir = os.getcwd() + os.sep
    return rsync_project(remote_dir=env.proj_path, local_dir=local_dir,
                         exclude=excludes)


def vcs_upload():
    """
    Uploads the project with the selected VCS tool.
    """
    if env.deploy_tool == "git":
        remote_path = "ssh://%s@%s%s" % (env.user, env.host_string,
                                         env.repo_path)
        if not exists(env.repo_path):
            run("mkdir -p %s" % env.repo_path)
            with cd(env.repo_path):
                run("git init --bare")
        local("git push -f %s master" % remote_path)
        with cd(env.repo_path):
            run("GIT_WORK_TREE=%s git checkout -f master" % env.proj_path)
            run("GIT_WORK_TREE=%s git reset --hard" % env.proj_path)
    elif env.deploy_tool == "hg":
        remote_path = "ssh://%s@%s/%s" % (env.user, env.host_string,
                                          env.repo_path)
        with cd(env.repo_path):
            if not exists("%s/.hg" % env.repo_path):
                run("hg init")
                print(env.repo_path)
            with fab_settings(warn_only=True):
                push = local("hg push -f %s" % remote_path)
                if push.return_code == 255:
                    abort()
            run("hg update")


def db_pass():
    """
    Prompts for the database password if unknown.
    """
    if not env.db_pass:
        env.db_pass = getpass("Enter the database password: ")
    return env.db_pass


@task
def apt(packages):
    """
    Installs one or more system packages via apt.
    """
    return sudo("apt-get install -y -q " + packages)


@task
def pip(packages):
    """
    Installs one or more Python packages within the virtual environment.
    """
    with virtualenv():
        return run("pip install %s" % packages)


def postgres(command):
    """
    Runs the given command as the postgres user.
    """
    show = not command.startswith("psql")
    return sudo(command, show=show, user="postgres")


@task
def psql(sql, show=True):
    """
    Runs SQL against the project's database.
    """
    out = postgres('psql -c "%s"' % sql)
    if show:
        print_command(sql)
    return out


@task
def backup(filename):
    """
    Backs up the project database.
    """
    tmp_file = "/tmp/%s" % filename
    # We dump to /tmp because user "postgres" can't write to other user folders
    postgres("pg_dump -Fc %s > %s" % (env.proj_name, tmp_file))
    run("cp %s ." % tmp_file)
    sudo("rm -f %s" % tmp_file)


@task
def backup_static(filename="static.tar", no_directory_structure=False):
    static_dir = static()
    if exists(static_dir):
        if no_directory_structure:
            run("tar -cf %s --exclude='*.thumbnails' -C %s ." % (filename,
                                                                 static_dir))
        else:
            run("tar -cf %s --exclude='*.thumbnails' %s" % (filename,
                                                            static_dir))

@task
def restore(filename, drop_first=False):
    """
    Restores the database.
    drop_first is needed for syncing to avoid Postgres errors
    """
    if drop_first:
        return postgres("pg_restore -c -C -d %s %s" % (env.proj_name, filename))  
    return postgres("pg_restore -c -d %s %s" % (env.proj_name, filename))


@task
def python(code, show=True):
    """
    Runs Python code in the project's virtual environment, with Django loaded.
    """
    setup = "import os;" \
            "os.environ[\'DJANGO_SETTINGS_MODULE\']=\'%s.settings\';" \
            "import django;" \
            "django.setup();" % env.proj_app
    full_code = 'python -c "%s%s"' % (setup, code.replace("`", "\\\`"))
    with project():
        if show:
            print_command(code)
        result = run(full_code, show=False)
    return result


def static():
    """
    Returns the live STATIC_ROOT directory.
    """
    return python("from django.conf import settings;"
                  "print(settings.STATIC_ROOT)", show=False).split("\n")[-1]


@task
def manage(command):
    """
    Runs a Django management command.
    """
    return run("%s %s" % (env.manage, command))


###########################
# Security best practices #
###########################

@task
@log_call
@hosts(["root@%s" % host for host in env.hosts])
def secure(new_user=env.user):
    """
    Minimal security steps for brand new servers.
    Installs system updates, creates new user (with sudo privileges) for future
    usage, and disables root login via SSH.
    """
    run("apt-get update -q")
    run("apt-get upgrade -y -q")
    run("adduser --gecos '' %s" % new_user)
    run("usermod -G sudo %s" % new_user)
    run("sed -i 's:RootLogin yes:RootLogin no:' /etc/ssh/sshd_config")
    run("service ssh restart")
    print(green("Security steps completed. Log in to the server as '%s' from "
                "now on." % new_user, bold=True))


#########################
# Install and configure #
#########################

@task
@log_call
def install():
    """
    Installs the base system and Python requirements for the entire server.
    """
    # Install system requirements
    sudo("apt-get update -y -q")
    apt("nginx libjpeg-dev python-dev python-setuptools git-core "
        "postgresql libpq-dev memcached supervisor python-pip")
    run("mkdir -p /home/%s/logs" % env.user)

    # Install Python requirements
    sudo("pip install -U pip virtualenv virtualenvwrapper mercurial")

    # Set up virtualenv
    run("mkdir -p %s" % env.venv_home)
    run("echo 'export WORKON_HOME=%s' >> /home/%s/.bashrc" % (env.venv_home,
                                                              env.user))
    run("echo 'source /usr/local/bin/virtualenvwrapper.sh' >> "
        "/home/%s/.bashrc" % env.user)
    print(green("Successfully set up git, mercurial, pip, virtualenv, "
                "supervisor, memcached.", bold=True))


@task
@log_call
def create():
    """
    Creates the environment needed to host the project.
    The environment consists of: system locales, virtualenv, database, project
    files, SSL certificate, and project-specific Python requirements.
    """
    # Generate project locale
    locale = env.locale.replace("UTF-8", "utf8")
    with hide("stdout"):
        if locale not in run("locale -a"):
            sudo("locale-gen %s" % env.locale)
            sudo("update-locale %s" % env.locale)
            sudo("service postgresql restart")
            run("exit")

    # Create project path
    run("mkdir -p %s" % env.proj_path)

    # Set up virtual env
    run("mkdir -p %s" % env.venv_home)
    with cd(env.venv_home):
        if exists(env.proj_name):
            if confirm("Virtualenv already exists in host server: %s"
                       "\nWould you like to replace it?" % env.proj_name):
                run("rm -rf %s" % env.proj_name)
            else:
                abort('Aborting')
        run("virtualenv %s" % env.proj_name)

    # Upload project files
    if env.deploy_tool in env.vcs_tools:
        vcs_upload()
    else:
        rsync_upload()

    # Create DB and DB user
    pw = db_pass()
    user_sql_args = (env.proj_name, pw.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    psql(user_sql, show=False)
    shadowed = "*" * len(pw)
    print_command(user_sql.replace("'%s'" % pw, "'%s'" % shadowed))
    psql("CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env.proj_name, env.proj_name, env.locale, env.locale))

    # Set up SSL certificate
    if not env.ssl_disabled:
        conf_path = "/etc/nginx/conf"
        if not exists(conf_path):
            sudo("mkdir %s" % conf_path)
        with cd(conf_path):
            crt_file = env.proj_name + ".crt"
            key_file = env.proj_name + ".key"
            if not exists(crt_file) and not exists(key_file):
                try:
                    crt_local, = glob(join("deploy", "*.crt"))
                    key_local, = glob(join("deploy", "*.key"))
                except ValueError:
                    parts = (crt_file, key_file, env.domains[0])
                    sudo("openssl req -new -x509 -nodes -out %s -keyout %s "
                         "-subj '/CN=%s' -days 3650" % parts)
                else:
                    upload_template(crt_local, crt_file, use_sudo=True)
                    upload_template(key_local, key_file, use_sudo=True)

    # Install project-specific requirements
    upload_template_and_reload("settings")
    with project():
        if env.reqs_path:
            pip("-r %s/%s" % (env.proj_path, env.reqs_path))
        pip("gunicorn setproctitle psycopg2 "
            "django-compressor python-memcached")
    # Bootstrap the DB
        manage("createdb --noinput --nodata")
        python("from django.conf import settings;"
               "from django.contrib.sites.models import Site;"
               "Site.objects.filter(id=settings.SITE_ID).update(domain='%s');"
               % env.domains[0])
        for domain in env.domains:
            python("from django.contrib.sites.models import Site;"
                   "Site.objects.get_or_create(domain='%s');" % domain)
        if env.admin_pass:
            pw = env.admin_pass
            user_py = ("from django.contrib.auth import get_user_model;"
                       "User = get_user_model();"
                       "u, _ = User.objects.get_or_create(username='admin');"
                       "u.is_staff = u.is_superuser = True;"
                       "u.set_password('%s');"
                       "u.save();" % pw)
            python(user_py, show=False)
            shadowed = "*" * len(pw)
            print_command(user_py.replace("'%s'" % pw, "'%s'" % shadowed))

    return True


@task
@log_call
def remove():
    """
    Blow away the current project.
    """
    if exists(env.venv_path):
        run("rm -rf %s" % env.venv_path)
    if exists(env.proj_path):
        run("rm -rf %s" % env.proj_path)
    for template in get_templates().values():
        remote_path = template["remote_path"]
        if exists(remote_path):
            sudo("rm %s" % remote_path)
    if exists(env.repo_path):
        run("rm -rf %s" % env.repo_path)
    sudo("supervisorctl update")
    psql("DROP DATABASE IF EXISTS %s;" % env.proj_name)
    psql("DROP USER IF EXISTS %s;" % env.proj_name)


##############
# Deployment #
##############

@task
@log_call
def restart():
    """
    Restart gunicorn worker processes for the project.
    If the processes are not running, they will be started.
    """
    pid_path = "%s/gunicorn.pid" % env.proj_path
    if exists(pid_path):
        run("kill -HUP `cat %s`" % pid_path)
    else:
        sudo("supervisorctl update")


@task
@log_call
def deploy():
    """
    Deploy latest version of the project.
    Backup current version of the project, push latest version of the project
    via version control or rsync, install new requirements, sync and migrate
    the database, collect any new static assets, and restart gunicorn's worker
    processes for the project.
    """
    if not exists(env.proj_path):
        if confirm("Project does not exist in host server: %s"
                   "\nWould you like to create it?" % env.proj_name):
            create()
        else:
            abort()

    # Backup current version of the project
    with cd(env.proj_path):
        backup("last.db")
    if env.deploy_tool in env.vcs_tools:
        with cd(env.repo_path):
            if env.deploy_tool == "git":
                    run("git rev-parse HEAD > %s/last.commit" % env.proj_path)
            elif env.deploy_tool == "hg":
                    run("hg id -i > last.commit")
        with project():
            backup_static()
    else:
        with cd(join(env.proj_path, "..")):
            excludes = ["*.pyc", "*.pio", "*.thumbnails"]
            exclude_arg = " ".join("--exclude='%s'" % e for e in excludes)
            run("tar -cf {0}.tar {1} {0}".format(env.proj_name, exclude_arg))

    # Deploy latest version of the project
    with update_changed_requirements():
        if env.deploy_tool in env.vcs_tools:
            vcs_upload()
        else:
            rsync_upload()
    with project():
        manage("collectstatic -v 0 --noinput")
        manage("syncdb --noinput")
        manage("migrate --noinput")
    for name in get_templates():
        upload_template_and_reload(name)
    restart()
    return True


@task
@log_call
def rollback():
    """
    Reverts project state to the last deploy.
    When a deploy is performed, the current state of the project is
    backed up. This includes the project files, the database, and all static
    files. Calling rollback will revert all of these to their state prior to
    the last deploy.
    """
    with update_changed_requirements():
        if env.deploy_tool in env.vcs_tools:
            with cd(env.repo_path):
                if env.deploy_tool == "git":
                        run("GIT_WORK_TREE={0} git checkout -f "
                            "`cat {0}/last.commit`".format(env.proj_path))
                elif env.deploy_tool == "hg":
                        run("hg update -C `cat last.commit`")
            with project():
                with cd(join(static(), "..")):
                    run("tar -xf %s/static.tar" % env.proj_path)
        else:
            with cd(env.proj_path.rsplit("/", 1)[0]):
                run("rm -rf %s" % env.proj_name)
                run("tar -xf %s.tar" % env.proj_name)
    with cd(env.proj_path):
        restore("last.db")
    restart()


def sync_transfer(to_env, to_dict, from_env, db_filename, static_filename):
    """
    Used by sync, backups static and db in current env, tranfers to to_env
    """

    to_user = to_dict['SSH_USER']
    to_host = to_dict['HOSTS'][0]
    
    print("%s: Preparing static directory and database for transfer" % from_env)

    backup(db_filename)
    backup_static(filename=static_filename, no_directory_structure=True)

    print('%s: Copying files to destination environment, %s' % (from_env,
                                                                to_env))
    run('scp %s %s@%s:~' % (db_filename, to_user, to_host))
    run('scp %s %s@%s:~' % (static_filename, to_user, to_host))

    # delete local copies of backups
    run('rm %s %s' % (db_filename, static_filename))


def sync_restore(to_env, from_env, db_filename, static_filename):
    with project():
        static_dir = static()

        print('%s: Backing up current static directory and database' % to_env)
        backup("last.db")
        backup_static()

        print('%s: Restoring to database copied from %s' % (to_env, from_env))
        restore('~/%s' % db_filename, drop_first=True)

        print('%s: Updating to static directory copied from %s' % (to_env,
                                                                   from_env))
        run('mkdir %s.new' % static_dir)
        run('tar -xf ~/%s -C %s.new' % (static_filename, static_dir))

        # rename current static
        run('mv %s %s.old' % (static_dir, static_dir))
        # move new static into place
        run('mv %s.new %s' % (static_dir, static_dir))

        # cleanup
        run('rm ~/%s' % db_filename)
        run('rm ~/%s' % static_filename)
        run('rm -rf %s.old' % static_dir)


@task
@log_call
def sync_to(to_env):
    """
    Syncs datbase and media from the current ENV to to_env
    """
    try:
        from_env = env.FABENV
    except AttributeError:
        abort('You must specify a FABENV, i.e. --set FABENV=ENVNAME')
    try:
        to_dict = fabric_dict[to_env]
    except KeyError:
        abort('ENV %s does not exist in the FABRIC dict' % to_env)

    if not confirm(
        red("You're about to overwrite the database and uploaded media in "
            "%s with database and uploaded media from %s. Are you "
            "sure?" % (to_env, from_env), bold=True)):
        abort("Sync canceled")

    current_dt_string = str(datetime.now()).replace(' ', '_').replace(':', '-')

    print("Syncing database and static files from %s to %s" % (from_env,
                                                               to_env))

    db_filename = '%s_transfer.db' % current_dt_string
    static_filename = '%s_transfer.tar' % current_dt_string

    execute(sync_transfer, to_env, to_dict, from_env,
            db_filename, static_filename)
    # switch to the desitination env
    setup_env(to_env)
    # using exexcute forces a new SSH connection for the new env setup
    execute(sync_restore, to_env, from_env, db_filename, static_filename)

    return True


@task
@log_call
def all():
    """
    Installs everything required on a new system and deploy.
    From the base software, up to the deployed project.
    """
    install()
    if create():
        deploy()
