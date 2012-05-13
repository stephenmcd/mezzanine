
import os
from functools import wraps
from getpass import getpass, getuser
from contextlib import contextmanager

from fabric.api import env, cd, prefix, sudo as _sudo, run as _run, hide
from fabric.contrib.files import exists, upload_template
from fabric.colors import yellow, green, blue, red

try:
    from settings import FABRIC as conf
except ImportError:
    conf = {}


################
# Config setup #
################

env.db_pass = conf.get("DB_PASS", None)
env.user = conf.get("SSH_USER", getuser())
env.password = conf.get("SSH_PASS", None)
env.key_filename = conf.get("SSH_KEY_PATH", None)
env.hosts = conf.get("HOSTS", [])

env.proj_name = conf.get("PROJECT_NAME", os.getcwd().split(os.sep)[-1])
env.venv_home = conf.get("VIRTUALENV_HOME", "/home/%s" % env.user)
env.venv_path = "%s/%s" % (env.venv_home, env.proj_name)
env.proj_dirname = "project"
env.proj_path = "%s/%s" % (env.venv_path, env.proj_dirname)

env.live_host = conf.get("LIVE_HOSTNAME", env.hosts[0])
env.repo_url = conf.get("REPO_URL", None)
env.reqs_path = conf.get("REQUIREMENTS_PATH", None)
env.gunicorn_port = conf.get("GUNICORN_PORT", 8000)
env.locale = conf.get("LOCALE", "en_US.utf8")


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
    _print(blue(">>> ", bold=True) +
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


def installed(command):
    """
    Check to see if the given command is installed on the remote server.
    """
    return run("which " + command)


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


def python(code):
    """
    Run Python code in the virtual environment, with the Django
    project loaded.
    """
    with project():
        return run('python -c "import os; '
                   'os.environ[\'DJANGO_SETTINGS_MODULE\'] = \'settings\'; '
                   '%s"' % code)


def manage(command):
    """
    Run a Django management command.
    """
    with project():
        return run("python manage.py %s" % command)


def locale():
    """
    Set the system locale.
    """
    return sudo("sudo update-locale LC_ALL=%s" % env.locale)


#########################
# System level installs #
#########################

@log_call
def install_base():
    """
    Install the base system-level and Python requirements for the
    entire server.
    """
    locale()
    sudo("apt-get update -y -q")
    apt("libjpeg-dev python-dev python-setuptools git-core")
    sudo("easy_install pip")
    sudo("pip install virtualenv mercurial")


@log_call
def install_nginx_base():
    """
    Install NGINX on the system.
    """
    apt("nginx")
    default_conf = "/etc/nginx/sites-enabled/default"
    if exists(default_conf):
        sudo("rm " + default_conf)


@log_call
def install_postgres_base():
    """
    Install PostgreSQL on the system.
    """
    locale()
    apt("postgresql libpq-dev")


@log_call
def install_memcached_base():
    """
    Install memcached on the system.
    """
    apt("memcached")


@log_call
def install_supervisor_base():
    """
    Install supervisor on the system.
    """
    apt("supervisor")


##########################
# Project level installs #
##########################

@log_call
def install_nginx_project():
    """
    Install NGINX configuration for the project.
    """
    path = "/etc/nginx/sites-enabled/%s.conf" % env.proj_name
    context = {
        "live_host": env.live_host,
        "static_root": env.proj_path,
        "project_name": env.proj_name,
        "gunicorn_port": env.gunicorn_port,
    }
    upload_template("deploy/nginx.conf", path, context, use_sudo=True)
    sudo("service nginx restart")


@log_call
def install_postgres_project():
    """
    Install a PostgreSQL database and user for the project.
    """
    password = db_pass()
    user_sql_args = (env.proj_name, password.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    psql(user_sql, show=False)
    shadowed = "*" * len(password)
    print_command(user_sql.replace("'%s'" % password, "'%s'" % shadowed))
    psql("CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env.proj_name, env.proj_name, env.locale, env.locale))


@log_call
def install_supervisor_project():
    """
    Install supervisor configuration for the project.
    """
    path = "/etc/supervisor/conf.d/%s.conf" % env.proj_name
    context = {
        "project_name": env.proj_name,
        "project_path": env.proj_path,
        "venv_path": env.venv_path,
        "user": env.user,
    }
    upload_template("deploy/supervisor.conf", path, context, use_sudo=True)
    sudo("supervisorctl reload")


#################
# Project setup #
#################

@log_call
def install_project():
    """
    Create a virtual environment, pull the project's repo from
    version control, add system-level configs for the project,
    and initialise the database with the live host.
    """
    with cd(env.venv_home):
        if exists(env.proj_name):
            remove = raw_input("\nVirtualenv exists: %s\nWould you like "
                               "to replace it? (yes/no) " % env.proj_name)
            if remove.lower() != "yes":
                print "\nAborting!"
                return False
            remove_project()
        run("virtualenv %s --distribute" % env.proj_name)
    with virtualenv():
        vcs = "git" if env.repo_url.startswith("git") else "hg"
        run("%s clone %s %s" % (vcs, env.repo_url, env.proj_dirname))
    install_nginx_project()
    install_postgres_project()
    install_supervisor_project()
    with project():
        path = "local_settings.py"
        context = {
            "db_name": env.proj_name,
            "db_user": env.proj_name,
            "db_pass": db_pass(),
        }
        upload_template("deploy/live_settings.py", path, context)
        path = "gunicorn.conf"
        context = {"port": env.gunicorn_port}
        upload_template("deploy/gunicorn.conf", path, context)
        if env.reqs_path:
            pip("-r %s/%s" % (env.proj_path, env.reqs_path))
        pip("gunicorn south psycopg2 python-memcached")
        manage("createdb --noinput")
        python("from django.conf import settings;"
               "from django.contrib.sites.models import Site;"
               "site, _ = Site.objects.get_or_create(id=settings.SITE_ID);"
               "site.domain = '" + env.live_host + "';"
               "site.save();")
    gunicorn_start()
    return True


######################
# Project management #
######################

@log_call
def gunicorn_start():
    """
    Start gunicorn for the project via supervisor.
    """
    sudo("supervisorctl start %s:gunicorn" % env.proj_name)


@log_call
def gunicorn_reload():
    """
    Restart gunicorn worker processes for the project.
    """
    with project():
        sudo("kill -HUP `cat gunicorn.pid`")


@log_call
def deploy():
    """
    Check out the latest version of the project from version
    control, install new requirements, sync andmigrate the database,
    collect any new static assets, and restart gunicorn's work
    processes for the project.
    """
    with project():
        git = env.repo_url.startswith("git")
        run("git pull" if git else "hg pull && hg up")
        if env.reqs_path:
            pip("-U -r %s/%s" % (env.proj_path, env.reqs_path))
        manage("syncdb --noinput")
        manage("migrate --noinput")
        manage("collectstatic -v 0 --noinput")
    gunicorn_reload()


@log_call
def remove_project():
    """
    Blow away the current project.
    """
    if exists(env.venv_path):
        sudo("rm -rf %s" % env.venv_path)
    for path in ("supervisor/conf.d", "nginx/sites-enabled"):
        full_path = "/etc/%s/%s.conf" % (path, env.proj_name)
        if exists(full_path):
            sudo("rm %s" % full_path)
    psql("DROP DATABASE %s;" % env.proj_name)
    psql("DROP USER %s;" % env.proj_name)


@log_call
def install_all():
    """
    Install everything required on a new system, from the base
    software, up to the deployed project.
    """
    install_base()
    install_nginx_base()
    install_postgres_base()
    install_memcached_base()
    install_supervisor_base()
    if install_project():
        deploy()
