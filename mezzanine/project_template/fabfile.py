
import os
import sys
from functools import wraps
from getpass import getpass, getuser
from glob import glob
from contextlib import contextmanager

from fabric.api import env, cd, prefix, sudo as _sudo, run as _run, hide
from fabric.contrib.files import exists, upload_template
from fabric.colors import yellow, green, blue, red


################
# Config setup #
################

conf = {}
if sys.argv[0].split(os.sep)[-1] == "fab":
    # Ensure we import settings from the current dir
    try:
        conf = __import__("settings", globals(), locals(), [], 0).FABRIC
        try:
            conf["HOSTS"][0]
        except (KeyError, ValueError):
            raise ImportError
    except (ImportError, AttributeError):
        print "Aborting, no hosts defined."
        exit()

env.db_pass = conf.get("DB_PASS", None)
env.admin_pass = conf.get("ADMIN_PASS", None)
env.user = conf.get("SSH_USER", getuser())
env.password = conf.get("SSH_PASS", None)
env.key_filename = conf.get("SSH_KEY_PATH", None)
env.hosts = conf.get("HOSTS", [])

env.proj_name = conf.get("PROJECT_NAME", os.getcwd().split(os.sep)[-1])
env.venv_home = conf.get("VIRTUALENV_HOME", "/home/%s" % env.user)
env.venv_path = "%s/%s" % (env.venv_home, env.proj_name)
env.proj_dirname = "project"
env.proj_path = "%s/%s" % (env.venv_path, env.proj_dirname)
env.manage = "%s/bin/python %s/project/manage.py" % (env.venv_path,
                                                     env.venv_path)
env.live_host = conf.get("LIVE_HOSTNAME", env.hosts[0] if env.hosts else None)
env.repo_url = conf.get("REPO_URL", None)
env.reqs_path = conf.get("REQUIREMENTS_PATH", None)
env.gunicorn_port = conf.get("GUNICORN_PORT", 8000)
env.locale = conf.get("LOCALE", "en_US.UTF-8")


##################
# Template setup #
##################

# Each template gets uploaded at deploy time, only if their
# contents has changed, in which case, the reload command is
# also run.

templates = {
    "nginx": {
        "local_path": "deploy/nginx.conf",
        "remote_path": "/etc/nginx/sites-enabled/%(proj_name)s.conf",
        "reload_command": "service nginx restart",
    },
    "supervisor": {
        "local_path": "deploy/supervisor.conf",
        "remote_path": "/etc/supervisor/conf.d/%(proj_name)s.conf",
        "reload_command": "supervisorctl reload",
    },
    "cron": {
        "local_path": "deploy/crontab",
        "remote_path": "/etc/cron.d/%(proj_name)s",
        "owner": "root",
        "mode": "600",
    },
    "gunicorn": {
        "local_path": "deploy/gunicorn.conf.py",
        "remote_path": "%(proj_path)s/gunicorn.conf.py",
    },
    "settings": {
        "local_path": "deploy/live_settings.py",
        "remote_path": "%(proj_path)s/local_settings.py",
    },
}


######################################
# Context for virtualenv and project #
######################################

@contextmanager
def virtualenv():
    """
    Run commands within the project's virtualenv.
    """
    with cd(env.venv_path):
        with prefix("source %s/bin/activate" % env.venv_path):
            yield


@contextmanager
def project():
    """
    Run commands within the project's directory.
    """
    with virtualenv():
        with cd(env.proj_dirname):
            yield


###########################################
# Utils and wrappers for various commands #
###########################################

def _print(output):
    print
    print output
    print


def print_command(command):
    _print(blue("$ ", bold=True) +
           yellow(command, bold=True) +
           red(" ->", bold=True))


def run(command, show=True):
    """
    Run a shell comand on the remote server.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _run(command)


def sudo(command, show=True):
    """
    Run a command as sudo.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _sudo(command)


def log_call(func):
    @wraps(func)
    def logged(*args, **kawrgs):
        header = "-" * len(func.__name__)
        _print(green("\n".join([header, func.__name__, header]), bold=True))
        return func(*args, **kawrgs)
    return logged


def get_templates():
    """
    Return each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected


def upload_template_and_reload(name):
    """
    Upload a template only if it has changed, and if so, reload a
    related service.
    """
    template = get_templates()[name]
    local_path = template["local_path"]
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


def db_pass():
    """
    Prompt for the database password if unknown.
    """
    if not env.db_pass:
        env.db_pass = getpass("Enter the database password: ")
    return env.db_pass


def apt(packages):
    """
    Install one or more system packages via apt.
    """
    return sudo("apt-get install -y -q " + packages)


def pip(packages):
    """
    Install one or more Python packages within the virtual environment.
    """
    with virtualenv():
        return sudo("pip install %s" % packages)


def psql(sql, show=True):
    """
    Run SQL against the project's database.
    """
    out = run('sudo -u root sudo -u postgres psql -c "%s"' % sql, show=False)
    if show:
        print_command(sql)
    return out


def python(code, show=True):
    """
    Run Python code in the virtual environment, with the Django
    project loaded.
    """
    setup = "import os; os.environ[\'DJANGO_SETTINGS_MODULE\']=\'settings\';"
    with project():
        return run('python -c "%s%s"' % (setup, code), show=False)
        if show:
            print_command(code)


def manage(command):
    """
    Run a Django management command.
    """
    return run("%s %s" % (env.manage, command))


#########################
# Install and configure #
#########################

@log_call
def install():
    """
    Install the base system-level and Python requirements for the
    entire server.
    """
    locale = "LC_ALL=%s" % env.locale
    with hide("stdout"):
        if locale not in sudo("cat /etc/default/locale"):
            sudo("update-locale %s" % locale)
            run("exit")
    sudo("apt-get update -y -q")
    apt("nginx libjpeg-dev python-dev python-setuptools git-core "
        "postgresql libpq-dev memcached supervisor")
    sudo("easy_install pip")
    sudo("pip install virtualenv mercurial")


@log_call
def create():
    """
    Create a virtual environment, pull the project's repo from
    version control, add system-level configs for the project,
    and initialise the database with the live host.
    """

    # Create virtualenv
    with cd(env.venv_home):
        if exists(env.proj_name):
            prompt = raw_input("\nVirtualenv exists: %s\nWould you like "
                               "to replace it? (yes/no) " % env.proj_name)
            if prompt.lower() != "yes":
                print "\nAborting!"
                return False
            remove()
        run("virtualenv %s --distribute" % env.proj_name)
        vcs = "git" if env.repo_url.startswith("git") else "hg"
        run("%s clone %s %s" % (vcs, env.repo_url, env.proj_path))

    # Create DB and DB user.
    pw = db_pass()
    user_sql_args = (env.proj_name, pw.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    psql(user_sql, show=False)
    shadowed = "*" * len(pw)
    print_command(user_sql.replace("'%s'" % pw, "'%s'" % shadowed))
    psql("CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env.proj_name, env.proj_name, env.locale, env.locale))

    # Set up SSL certificate.
    conf_path = "/etc/nginx/conf"
    if not exists(conf_path):
        sudo("mkdir %s" % conf_path)
    with cd(conf_path):
        crt_file = env.proj_name + ".crt"
        key_file = env.proj_name + ".key"
        if not exists(crt_file) and not exists(key_file):
            try:
                crt_local, = glob(os.path.join("deploy", "*.crt"))
                key_local, = glob(os.path.join("deploy", "*.key"))
            except ValueError:
                parts = (crt_file, key_file, env.live_host)
                sudo("openssl req -new -x509 -nodes -out %s -keyout %s "
                     "-subj '/CN=%s' -days 3650" % parts)
            else:
                upload_template(crt_file, crt_local, use_sudo=True)
                upload_template(key_file, key_local, use_sudo=True)

    # Set up project.
    upload_template_and_reload("settings")
    with project():
        if env.reqs_path:
            pip("-r %s/%s" % (env.proj_path, env.reqs_path))
        pip("gunicorn setproctitle south psycopg2 "
            "django-compressor python-memcached")
        manage("createdb --noinput")
        python("from django.conf import settings;"
               "from django.contrib.sites.models import Site;"
               "site, _ = Site.objects.get_or_create(id=settings.SITE_ID);"
               "site.domain = '" + env.live_host + "';"
               "site.save();")
        if env.admin_pass:
            pw = env.admin_pass
            user_py = ("from django.contrib.auth.models import User;"
                       "u, _ = User.objects.get_or_create(username='admin');"
                       "u.is_staff = u.is_superuser = True;"
                       "u.set_password('%s');"
                       "u.save();" % pw)
            python(user_py, show=False)
            shadowed = "*" * len(pw)
            print_command(user_py.replace("'%s'" % pw, "'%s'" % shadowed))

    return True


@log_call
def remove():
    """
    Blow away the current project.
    """
    if exists(env.venv_path):
        sudo("rm -rf %s" % env.venv_path)
    for template in get_templates().values():
        remote_path = template["remote_path"]
        if exists(remote_path):
            sudo("rm %s" % remote_path)
    psql("DROP DATABASE %s;" % env.proj_name)
    psql("DROP USER %s;" % env.proj_name)


##############
# Deployment #
##############

@log_call
def restart():
    """
    Restart gunicorn worker processes for the project.
    """
    pid_path = "%s/gunicorn.pid" % env.proj_path
    if exists(pid_path):
        sudo("kill -HUP `cat %s`" % pid_path)
    else:
        sudo("supervisorctl start %s:gunicorn" % env.proj_name)


@log_call
def deploy():
    """
    Check out the latest version of the project from version
    control, install new requirements, sync and migrate the database,
    collect any new static assets, and restart gunicorn's work
    processes for the project.
    """
    if not exists(env.venv_path):
        prompt = raw_input("\nVirtualenv doesn't exist: %s\nWould you like "
                           "to create it? (yes/no) " % env.proj_name)
        if prompt.lower() != "yes":
            print "\nAborting!"
            return False
        create()
    for name in get_templates():
        upload_template_and_reload(name)
    with project():
        git = env.repo_url.startswith("git")
        run("git pull -f" if git else "hg pull && hg up -C")
        if env.reqs_path:
            pip("-r %s/%s" % (env.proj_path, env.reqs_path))
        manage("syncdb --noinput")
        manage("migrate --noinput")
        manage("collectstatic -v 0 --noinput")
    restart()
    return True


@log_call
def all():
    """
    Install everything required on a new system, from the base
    software, up to the deployed project.
    """
    install()
    if create():
        deploy()
