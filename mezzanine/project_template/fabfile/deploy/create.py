from glob import glob

from future.builtins import input
from posixpath import join
from fabric.api import cd
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from .abstract_deploy import AbstractDeployTask
from .db import PsqlTask
from ..website import ManageTask, PythonTask
from .pip import PipTask
from .remove import RemoveTask


class CreateTask(AbstractDeployTask):
    """
    Create a new virtual environment for a project.
    Pulls the project's repo from version control, adds system-level
    configs for the project, and initialises the database with the
    live host.
    """
    name = "create"

    def run(self):
        # Create virtualenv
        with cd(self.env.venv_home):
            if exists(self.env.proj_name):
                prompt = input("\nVirtualenv exists: %s"
                               "\nWould you like to replace it? (yes/no) "
                               % self.env.proj_name)
                if prompt.lower() != "yes":
                    print("\nAborting!")
                    return False
                RemoveTask(self.env, self.templates).run()
            self.run_command("virtualenv %s --distribute" % self.env.proj_name)
            vcs = "git" if self.env.git else "hg"
            self.run_command("%s clone %s %s" % (
                vcs, self.env.repo_url, self.env.proj_path))

        # Create DB and DB user.
        pw = self.db_pass()
        user_sql_args = (self.env.proj_name, pw.replace("'", "\'"))
        user_sql = \
            "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
        psql_task = PsqlTask(self.env)
        psql_task.run(user_sql, show=False)
        shadowed = "*" * len(pw)
        self.print_command(user_sql.replace("'%s'" % pw, "'%s'" % shadowed))
        psql_task.run(
            "CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
            "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
            (self.env.proj_name, self.env.proj_name,
             self.env.locale, self.env.locale))

        # Set up SSL certificate.
        if not self.env.ssl_disabled:
            conf_path = "/etc/nginx/conf"
            if not exists(conf_path):
                self.as_sudo("mkdir %s" % conf_path)
            with cd(conf_path):
                crt_file = self.env.proj_name + ".crt"
                key_file = self.env.proj_name + ".key"
                if not exists(crt_file) and not exists(key_file):
                    try:
                        crt_local, = glob(join("deploy", "*.crt"))
                        key_local, = glob(join("deploy", "*.key"))
                    except ValueError:
                        parts = (crt_file, key_file, self.env.domains[0])
                        self.as_sudo(
                            "openssl req -new -x509 -nodes -out %s -keyout %s "
                            "-subj '/CN=%s' -days 3650" % parts)
                    else:
                        upload_template(crt_local, crt_file, use_sudo=True)
                        upload_template(key_local, key_file, use_sudo=True)

        # Set up project.
        self.upload_template_and_reload("settings")
        with self.project():
            pip_task = PipTask(self.env)
            if self.env.reqs_path:
                pip_task.run(
                    "-r %s/%s" % (self.env.proj_path, self.env.reqs_path))
            pip_task.run(
                "gunicorn setproctitle south psycopg2 "
                "django-compressor python-memcached")
            ManageTask(self.env).run(
                "createdb --noinput --nodata")
            python_task = PythonTask(self.env)
            python_task.run(
                "from django.conf import settings;"
                "from django.contrib.sites.models import Site;"
                "Site.objects.filter(id=settings.SITE_ID).update(domain='%s');"
                % self.env.domains[0])
            for domain in self.env.domains:
                PythonTask(self.env).run(
                    "from django.contrib.sites.models import Site;"
                    "Site.objects.get_or_create(domain='%s');" % domain)
            if self.env.admin_pass:
                pw = self.env.admin_pass
                user_py = (
                    "from mezzanine.utils.models import get_user_model;"
                    "User = get_user_model();"
                    "u, _ = User.objects.get_or_create(username='admin');"
                    "u.is_staff = u.is_superuser = True;"
                    "u.set_password('%s');"
                    "u.save();" % pw)
                python_task.run(user_py, show=False)
                shadowed = "*" * len(pw)
                self.print_command(
                    user_py.replace("'%s'" % pw, "'%s'" % shadowed))

        return True