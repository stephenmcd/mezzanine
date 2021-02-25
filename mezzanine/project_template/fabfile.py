import os
import re
import sys
from contextlib import contextmanager
from getpass import getpass, getuser
from glob import glob
from importlib import import_module
from posixpath import join
from mezzanine.utils.conf import real_project_name
from fabric import task
from invocations.console import confirm
from patchwork.files import exists
from patchwork.transfers import rsync as rsync_transfer


################
# Config setup #
################

env = {}
conf = {}
env['proj_app'] = real_project_name("{{ project_name }}")

if sys.argv[0].split(os.sep)[-1] in ("fab", "fab-script.py"):
    # Ensure we import settings from the current dir
    try:
        conf = import_module(f"{env['proj_app']}.settings").FABRIC
        try:
            conf["HOSTS"][0]
        except (KeyError, ValueError):
            raise ImportError
    except (ImportError, AttributeError):
        print("Aborting, no hosts defined.")
        exit()

# Connection Config
env['db_pass'] = conf.get("DB_PASS", None)
env['admin_pass'] = conf.get("ADMIN_PASS", None)
env['user'] = conf.get("SSH_USER", getuser())
env['password'] = conf.get("SSH_PASS", None)
env['key_filename'] = conf.get("SSH_KEY_PATH", None)
env['hosts'] = conf.get("HOSTS", [""])
host_list = [f"{env['user']}@{env['hosts'][0]}"]

# Project Config
env['proj_name'] = conf.get("PROJECT_NAME", env['proj_app'])
env['venv_home'] = conf.get("VIRTUALenv['HOME']", "/home/%s/.virtualenvs" % env['user'])
env['venv_path'] = join(env['venv_home'], env['proj_name'])
env['proj_path'] = "/home/%s/mezzanine/%s" % (env['user'], env['proj_name'])
env['manage'] = "%s/bin/python %s/manage.py" % (env['venv_path'], env['proj_path'])
env['domains'] = conf.get("DOMAINS", [conf.get("LIVE_HOSTNAME", env['hosts'][0])])
env['domains_nginx'] = " ".join(env['domains'])
env['domains_regex'] = "|".join(env['domains'])
env['domains_python'] = ", ".join(["'%s'" % s for s in env['domains']])
env['ssl_disabled'] = "#" if len(env['domains']) > 1 else ""
env['vcs_tools'] = ["git", "hg"]
env['deploy_tool'] = conf.get("DEPLOY_TOOL", "rsync")
env['reqs_path'] = conf.get("REQUIREMENTS_PATH", None)
env['locale'] = conf.get("LOCALE", "en_US.UTF-8")
env['num_workers'] = conf.get("NUM_WORKERS", "multiprocessing.cpu_count() * 2 + 1")
env['secret_key'] = conf.get("SECRET_KEY", "")
env['nevercache_key'] = conf.get("NEVERCACHE_KEY", "")

# Remote git repos need to be "bare" and reside separated from the project
if env['deploy_tool'] == "git":
    env['repo_path'] = "/home/%s/git/%s.git" % (env['user'], env['proj_name'])
else:
    env['repo_path'] = env['proj_path']


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
        "reload_command": "su -c \'nginx -t && systemctl restart nginx\'",
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
def virtualenv(c):
    """
    Runs commands within the project's virtualenv.
    """
    with c.cd(env['venv_path']):
        with c.prefix("source %s/bin/activate" % env['venv_path']):
            yield


@contextmanager
def project(c):
    """
    Runs commands within the project's directory.
    """
    with virtualenv(c):
        with c.cd(env['proj_path']):
            yield


@contextmanager
def update_changed_requirements(c):
    """
    Checks for changes in the requirements file across an update,
    and gets new requirements if changes have occurred.
    """
    reqs_path = join(env['proj_path'], env['reqs_path'])
    get_reqs = lambda: run(c, f"cat {reqs_path}", show=False).stdout
    old_reqs = get_reqs() if env['reqs_path'] else ""
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
        pip(c, f"-r {env['proj_path']}/{env['reqs_path']}")


###########################################
# Utils and wrappers for various commands #
###########################################

def _print(output):
    print(f'\n{output} \n')


def print_command(command):
    _print(colorize("$ ", fg='blue')
           + colorize(command, fg='yellow')
           + colorize(" ->", fg='green'))


def colorize(text, fg='green', bg='black', style='bold'):
    colors = dict(black=0, red=1, green=2, yellow=3, blue=4)
    styles = dict(reset=0, bold=1, underscore=4, underline=4)
    return f'\033[3{colors[fg]};4{colors[bg]};{styles[style]}m{text}\033[0m'


def abort(message):
    message = colorize(message, fg='red')
    print(f'\n{message} \n')
    sys.exit(1)


@task(hosts=host_list)
def run(c, command, show=True, *args, **kwargs):
    """
    Runs a shell comand on the remote server.
    """
    if show:
        print_command(command)
    return c.run(command, *args, **kwargs)


@task(hosts=host_list)
def sudo(c, command, show=True, *args, **kwargs):
    """
    Runs a command as sudo on the remote server.
    """
    sudo_pass(c)
    if show:
        print_command(f'sudo {command}')
    return c.sudo(command, *args, **kwargs)


def log_call():
    task_name = sys._getframe(1).f_code.co_name
    header = "-" * len(task_name)
    _print(colorize("\n".join([header, task_name, header])))


def get_templates():
    """
    Returns each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected


def upload_template_and_reload(c, name):
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
    if exists(c, remote_path):
        remote_data = sudo(c, f"cat {remote_path}",
                           show=False, hide='stdout').stdout
    with open(local_path, "r") as f:
        local_data = f.read()
        # Escape all non-string-formatting-placeholder occurrences of '%':
        local_data = re.sub(r"%(?!\(\w+\)s)", "%%", local_data)
        if "%(db_pass)s" in local_data:
            env['db_pass'] = db_pass()
        local_data %= env
    clean = lambda s: s.replace("\n", "").replace("\r", "").strip()
    if clean(remote_data) == clean(local_data):
        return

    tmp_local_path = f'{local_path}.tmp'
    with open(tmp_local_path, "w", encoding='utf-8') as temp:
        temp.write(local_data)
    rsync(c, tmp_local_path, remote_path, use_sudo=True)
    if owner:
        sudo(c, "chown %s %s" % (owner, remote_path))
    if mode:
        sudo(c, "chmod %s %s" % (mode, remote_path))
    if reload_command:
        sudo(c, reload_command)


def rsync(c, source, target, exclude=[], use_sudo=False):
    """
    Wrapper around patchwork rsync to add sudo support
    """
    c.connect_kwargs["key_filename"] = env['key_filename']
    if not use_sudo:
        rsync_transfer(c, source, target, exclude)
    else:
        if source[-1] == '/':
            tmp_target = f"/tmp/{source.split('/')[-2]}"
        else:
            tmp_target = f"/tmp/{source.split('/')[-1]}"
        rsync_transfer(c, source, tmp_target, exclude)
        sudo(c, f"cp -rfp {tmp_target} {target}")
        sudo(c, f"rm -rf {tmp_target}")


def rsync_upload(c):
    """
    Uploads the project with rsync excluding some files and folders.
    """
    excludes = [
        "*.pyc",
        "*.pyo",
        "*.db",
        ".DS_Store",
        ".coverage",
        "local_settings.py",
        "/static",
        "/.git",
        "/.hg",
    ]
    local_dir = os.getcwd() + os.sep
    return rsync(c, source=local_dir, target=env['proj_path'],
                 exclude=excludes)


def vcs_upload(c):
    """
    Uploads the project with the selected VCS tool.
    """
    if env['deploy_tool'] == "git":
        remote_path = f"ssh://{env['user']}@{env['host_string']}\
                       {env['repo_path']}"
        if not exists(c, env['repo_path']):
            run(c, f"mkdir -p {env['repo_path']}")
            with c.cd(env['repo_path']):
                run(c, "git init --bare")
        c.local("git push -f {remote_path} master")
        with c.cd(env['repo_path']):
            run(c, "GIT_WORK_TREE={env['proj_path']} git checkout -f master")
            run(c, "GIT_WORK_TREE={env['proj_path']} git reset --hard")
    elif env['deploy_tool'] == "hg":
        remote_path = "ssh://%s@%s/%s" % (env['user'], env['host_string'],
                                          env['repo_path'])
        with c.cd(env['repo_path']):
            if not exists(c, f"{env['repo_path']}/.hg"):
                run("hg init")
                print(env['repo_path'])
            push = c.local(f"hg push -f {remote_path}")
            if push.return_code == 255:
                abort("Aborting.")
            run(c, "hg update")


def sudo_pass(c):
    """
    Prompts for the sudo password if unknown.
    """
    if not c.config.sudo.password:
        c.config.sudo.password = getpass("Enter sudo password: ")
    return c.config.sudo.password


def db_pass():
    """
    Prompts for the database password if unknown.
    """
    if not env['db_pass']:
        env['db_pass'] = getpass("Enter the database password: ")
    return env['db_pass']


@task(hosts=host_list)
def apt(c, packages):
    """
    Installs one or more system packages via apt.
    """
    return sudo(c, f"apt-get install -y -q {packages}")


@task(hosts=host_list)
def pip(c, packages):
    """
    Installs one or more Python packages within the virtual environment.
    """
    with virtualenv(c):
        return run(c, "pip install %s" % packages)


def postgres(c, command):
    """
    Runs the given command as the postgres user.
    """
    show = not command.startswith("psql")
    return sudo(c, command, show=show, user="postgres")


@task(hosts=host_list)
def psql(c, sql, show=True):
    """
    Runs SQL against the project's database.
    """
    out = postgres(c, 'psql -c "%s"' % sql)
    if show:
        print_command(sql)
    return out


@task(hosts=host_list)
def backup(c, filename):
    """
    Backs up the project database.
    """
    tmp_file = "/tmp/%s" % filename
    # We dump to /tmp because user "postgres" can't write to other user folders
    postgres(c, "pg_dump -Fc %s > %s" % (env['proj_name'], tmp_file))
    with c.cd(env['proj_path']):
        run(c, "cp %s ." % tmp_file)
        run(c, "rm -f %s" % tmp_file)


@task(hosts=host_list)
def restore(c, filename):
    """
    Restores the project database from a previous backup.
    """
    return postgres(c, "pg_restore -c -d %s %s" % (env['proj_name'], filename))


@task(hosts=host_list)
def python(c, code, show=True):
    """
    Runs Python code in the project's virtual environment, with Django loaded.
    """
    setup = "import os;" \
            "os.environ[\'DJANGO_SETTINGS_MODULE\']=\'%s.settings\';" \
            "import django;" \
            "django.setup();" % env['proj_app']
    full_code = 'python -c "%s%s"' % (setup, code.replace("`", "\\\`"))
    with project(c):
        if show:
            print_command(code)
        result = run(c, full_code, show=False)
    return result


def static(c):
    """
    Returns the live STATIC_ROOT directory.
    """
    return python(c, "from django.conf import settings;"
                  "print(settings.STATIC_ROOT)", show=False).split("\n")[-1]


@task(hosts=host_list)
def manage(c, command):
    """
    Runs a Django management command.
    """
    return run(c, "%s %s" % (env['manage'], command))


###########################
# Security best practices #
###########################

@task(hosts=[f"root@{host}" for host in env["hosts"]])
def secure(c, new_user=env['user']):
    """
    Minimal security steps for brand new servers.
    Installs system updates, creates new user (with sudo privileges) for future
    usage, and disables root login via SSH.
    """
    log_call()
    run(c, "apt-get update -q")
    run(c, "apt-get upgrade -y -q")
    add_result = run(c, "adduser --shell /bin/bash --gecos '' %s" % new_user)
    run(c, "usermod -G sudo %s" % new_user)
    if "error" not in add_result.stderr.lower():
        run(c, "sed -i 's:RootLogin yes:RootLogin no:' /etc/ssh/sshd_config")
        run(c, "service ssh restart")
        print(colorize(f"Security steps completed.\
                        \nLog in to the server as '{new_user}' from now on."))
    else:
        abort(f'Aborting with SSH root login enabled!\
                \nDetected possible errors while adding user: {new_user}')


#########################
# Install and configure #
#########################

@task(hosts=host_list)
def install(c):
    """
    Installs the base system and Python requirements for the entire server.
    """
    log_call()
    # Install system requirements
    sudo(c, "apt-get update -y -q")
    apt(c, "nginx libjpeg-dev python3-dev python3-setuptools git-core "
        "postgresql libpq-dev memcached supervisor python3-pip")
    run(c, "mkdir -p /home/%s/logs" % env['user'])

    # Install Python requirements
    sudo(c, "pip3 install -U pip")
    sudo(c, "pip3 install -U virtualenv virtualenvwrapper mercurial")

    # Set up virtualenv
    run(c, "mkdir -p %s" % env['venv_home'])
    run(c, "echo 'export WORKON_HOME=%s' >> /home/%s/.bashrc" % (env['venv_home'],
                                                                 env['user']))
    run(c, "echo 'source /usr/local/bin/virtualenvwrapper.sh' >> "
        "/home/%s/.bashrc" % env['user'])
    print(colorize("Successfully set up git, mercurial, pip, virtualenv, "
                   "supervisor, memcached."))


@task(hosts=host_list)
def create(c):
    """
    Creates the environment needed to host the project.
    The environment consists of: system locales, virtualenv, database, project
    files, SSL certificate, and project-specific Python requirements.
    """
    log_call()
    # Generate project locale
    locale = env['locale'].replace("UTF-8", "utf8")
    if locale not in run(c, "locale -a", hide='stdout').stdout:
        sudo(c, f"locale-gen {env['locale']}", hide='stdout')
        sudo(c, f"update-locale {env['locale']}", hide='stdout')
        sudo(c, "service postgresql restart", hide='stdout')
        run(c, "exit")

    # Create project path
    run(c, f"mkdir -p {env['proj_path']}")

    # Set up virtual env
    run(c, f"mkdir -p {env['venv_home']}")
    with c.cd(env['venv_home']):
        if exists(c, env['proj_name']):
            if confirm("Virtualenv already exists in host server: %s"
                       "\nWould you like to replace it?" % env['proj_name']):
                run(c, "rm -rf %s" % env['proj_name'])
            else:
                print("Aborting.")
        run(c, f"virtualenv {env['proj_name']}")

    # Upload project files
    if env['deploy_tool'] in env['vcs_tools']:
        vcs_upload(c)
    else:
        rsync_upload(c)

    # Create DB and DB user
    pw = db_pass()
    user_sql_args = (env['proj_name'], pw.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    psql(c, user_sql, show=False)
    shadowed = "*" * len(pw)
    print_command(user_sql.replace("'%s'" % pw, "'%s'" % shadowed))
    psql(c, "CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env['proj_name'], env['proj_name'], env['locale'], env['locale']))

    # Set up SSL certificate
    if not env['ssl_disabled']:
        conf_path = "/etc/nginx/conf"
        if not exists(c, conf_path):
            sudo(c, "mkdir %s" % conf_path)
        with c.cd(conf_path):
            crt_file = env['proj_name'] + ".crt"
            key_file = env['proj_name'] + ".key"
            if not exists(c, crt_file) and not exists(c, key_file):
                try:
                    crt_local, = glob(join("deploy", "*.crt"))
                    key_local, = glob(join("deploy", "*.key"))
                except ValueError:
                    parts = (crt_file, key_file, env['domains'][0])
                    sudo(c, "openssl req -new -x509 -nodes -out %s -keyout %s "
                         "-subj '/CN=%s' -days 3650" % parts)
            else:
                rsync(c, crt_local, crt_file, use_sudo=True)
                rsync(c, key_local, key_file, use_sudo=True)

    # Install project-specific requirements
    upload_template_and_reload(c, "settings")
    with project(c):
        if env['reqs_path']:
            pip(c, "-r %s/%s" % (env['proj_path'], env['reqs_path']))
        pip(c, "gunicorn setproctitle psycopg2 "
            "django-compressor python-memcached")
    # Bootstrap the DB
        manage(c, "createdb --noinput --nodata")
        python(c, "from django.conf import settings;"
               "from django.contrib.sites.models import Site;"
               "Site.objects.filter(id=settings.SITE_ID).update(domain='%s');"
               % env['domains'][0])
        for domain in env['domains']:
            python(c, "from django.contrib.sites.models import Site;"
                   "Site.objects.get_or_create(domain='%s');" % domain)
        if env['admin_pass']:
            pw = env['admin_pass']
            user_py = ("from django.contrib.auth import get_user_model;"
                       "User = get_user_model();"
                       "u, _ = User.objects.get_or_create(username='admin');"
                       "u.is_staff = u.is_superuser = True;"
                       "u.set_password('%s');"
                       "u.save();" % pw)
            python(c, user_py, show=False)
            shadowed = "*" * len(pw)
            print_command(user_py.replace("'%s'" % pw, "'%s'" % shadowed))

    return True


@task(hosts=host_list)
def remove(c):
    """
    Blow away the current project.
    """
    log_call()
    if exists(c, env['venv_path']):
        run(c, "rm -rf %s" % env['venv_path'])
    if exists(c, env['proj_path']):
        run(c, "rm -rf %s" % env['proj_path'])
    for template in get_templates().values():
        remote_path = template["remote_path"]
        if exists(c, remote_path):
            sudo(c, "rm %s" % remote_path)
    if exists(c, env['repo_path']):
        run(c, "rm -rf %s" % env['repo_path'])
    sudo(c, "supervisorctl update")
    psql(c, "DROP DATABASE IF EXISTS %s;" % env['proj_name'])
    psql(c, "DROP USER IF EXISTS %s;" % env['proj_name'])


##############
# Deployment #
##############

@task(hosts=host_list)
def restart(c):
    """
    Restart gunicorn worker processes for the project.
    If the processes are not running, they will be started.
    """
    log_call()
    pid_path = "%s/gunicorn.pid" % env['proj_path']
    if exists(c, pid_path):
        run(c, "kill -HUP `cat %s`" % pid_path)
    else:
        sudo(c, "supervisorctl update")


@task(hosts=host_list)
def deploy(c):
    """
    Deploy latest version of the project.
    Backup current version of the project, push latest version of the project
    via version control or rsync, install new requirements, sync and migrate
    the database, collect any new static assets, and restart gunicorn's worker
    processes for the project.
    """
    log_call()
    if not exists(c, env['proj_path']):
        if confirm("Project does not exist in host server: {env['proj_name']}"
                   "\nWould you like to create it?"):
            create(c)
        else:
            abort('Aborting!')

    # Backup current version of the project
    backup(c, "last.db")
    if env['deploy_tool'] in env['vcs_tools']:
        with c.cd(env['repo_path']):
            if env['deploy_tool'] == "git":
                run(c, "git rev-parse HEAD > %s/last.commit" % env['proj_path'])
            elif env['deploy_tool'] == "hg":
                run(c, "hg id -i > last.commit")
        with project(c):
            static_dir = static(c)
            if exists(c, static_dir):
                run(c, "tar -cf static.tar --exclude='*.thumbnails' %s" %
                    static_dir)
    else:
        with c.cd(join(env['proj_path'], "..")):
            excludes = ["*.pyc", "*.pio", "*.thumbnails"]
            exclude_arg = " ".join("--exclude='%s'" % e for e in excludes)
            run(c, "tar -cf {0}.tar {1} {0}".format(env['proj_name'], exclude_arg))

    # Deploy latest version of the project
    with update_changed_requirements(c):
        if env['deploy_tool'] in env['vcs_tools']:
            vcs_upload(c)
        else:
            rsync_upload(c)
    with project(c):
        manage(c, "collectstatic -v 0 --noinput")
        manage(c, "migrate --noinput")
    for name in get_templates():
        upload_template_and_reload(c, name)
    restart(c)
    return True


@task(hosts=host_list)
def rollback(c):
    """
    Reverts project state to the last deploy.
    When a deploy is performed, the current state of the project is
    backed up. This includes the project files, the database, and all static
    files. Calling rollback will revert all of these to their state prior to
    the last deploy.
    """
    log_call()
    with update_changed_requirements():
        if env['deploy_tool'] in env['vcs_tools']:
            with c.cd(env['repo_path']):
                if env['deploy_tool'] == "git":
                    run("GIT_WORK_TREE={0} git checkout -f "
                        "`cat {0}/last.commit`".format(env['proj_path']))
                elif env['deploy_tool'] == "hg":
                    run("hg update -C `cat last.commit`")
            with project(c):
                with c.cd(join(static(c), "..")):
                    run("tar -xf %s/static.tar" % env['proj_path'])
        else:
            with c.cd(env['proj_path'].rsplit("/", 1)[0]):
                run("rm -rf %s" % env['proj_name'])
                run("tar -xf %s.tar" % env['proj_name'])
    with c.cd(env['proj_path']):
        restore("last.db")
    restart(c)


@task(hosts=host_list)
def all(c):
    """
    Installs everything required on a new system and deploy.
    From the base software, up to the deployed project.
    """
    log_call()
    install(c)
    if create(c):
        deploy(c)
