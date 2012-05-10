
import os
from getpass import getpass, getuser
from contextlib import contextmanager

from fabric.api import env, cd, prefix, sudo as _sudo, run as _run, hide
from fabric.contrib.files import exists, upload_template

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
    with cd(env.venv_path):
        with prefix("source %s/bin/activate" % env.venv_path):
            yield


@contextmanager
def project():
    with virtualenv():
        with cd(env.proj_dirname):
            yield


###########################################
# Utils and wrappers for various commands #
###########################################

def sudo(command):
    return _sudo(command)


def run(command):
    return _run(command)


def installed(command):
    return run("which " + command)


def db_pass():
    if not env.db_pass:
        env.db_pass = getpass("Enter the database password: ")
    return env.db_pass


def apt(packages):
    return sudo("apt-get install -y -q " + packages)


def pip(packages):
    with virtualenv():
        return sudo("pip install %s" % packages)


def psql(sql):
    return run('sudo -u root sudo -u postgres psql -c "%s"' % sql)


def python(code):
    with project():
        return run('python -c "import os; '
                   'os.environ[\'DJANGO_SETTINGS_MODULE\'] = \'settings\'; '
                   '%s"' % code)


def locale():
    return sudo("sudo update-locale LC_ALL=%s" % env.locale)


def manage(command):
    with project():
        return run("python manage.py %s" % command)


#########################
# System level installs #
#########################

def install_base():
    locale()
    sudo("apt-get update -y -q")
    apt("libjpeg-dev python-dev python-setuptools git-core")
    sudo("easy_install pip")
    sudo("pip install virtualenv mercurial")


def install_nginx_base():
    apt("nginx")
    default_conf = "/etc/nginx/sites-enabled/default"
    if exists(default_conf):
        sudo("rm " + default_conf)


def install_postgres_base():
    locale()
    apt("postgresql libpq-dev")


def install_memcached_base():
    apt("memcached")


def install_supervisor_base():
    apt("supervisor")


##########################
# Project level installs #
##########################

def install_nginx_project():
    path = "/etc/nginx/sites-enabled/%s.conf" % env.proj_name
    context = {
        "live_host": env.live_host,
        "static_root": env.proj_path,
        "project_name": env.proj_name,
        "gunicorn_port": env.gunicorn_port,
    }
    upload_template("deploy/nginx.conf", path, context, use_sudo=True)
    sudo("service nginx restart")


def install_postgres_project():
    password = db_pass()
    user_sql_args = (env.proj_name, password.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    with hide("running"):
        psql(user_sql)
    print user_sql.replace("'%s'" % password, "'%s'" % ("*" * len(password)))
    psql("CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env.proj_name, env.proj_name, env.locale, env.locale))


def install_supervisor_project():
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

def install_project():
    with cd(env.venv_home):
        if exists(env.proj_name):
            print "Aborting, virtualenv exists: %s" % env.proj_name
            return False
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

def gunicorn_start():
    sudo("supervisorctl start %s:gunicorn" % env.proj_name)


def gunicorn_reload():
    with project():
        sudo("kill -HUP `cat gunicorn.pid`")


def deploy():
    with project():
        git = env.repo_url.startswith("git")
        run("git pull" if git else "hg pull && hg up")
        if env.reqs_path:
            pip("-U -r %s/%s" % (env.proj_path, env.reqs_path))
        manage("syncdb --noinput")
        manage("migrate --noinput")
        manage("collectstatic -v 0 --noinput")
    gunicorn_reload()


def install_all():
    install_base()
    install_nginx_base()
    install_postgres_base()
    install_memcached_base()
    install_supervisor_base()
    if install_project():
        deploy()
