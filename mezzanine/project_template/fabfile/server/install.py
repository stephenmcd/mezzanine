from fabric.api import hide

from .abstract_server import AbstractServerTask
from .apt import AptTask

class InstallTask(AbstractServerTask):
    """
    Installs the base system and Python requirements for the entire server.
    """
    name = "install"

    def __init__(self, environment, *args, **kwargs):
        super(AbstractServerTask, self).__init__(*args, **kwargs)
        self.env = environment

    def run(self):
        locale = "LC_ALL=%s" % self.env.locale

        with hide("stdout"):
            if locale not in self.as_sudo("cat /etc/default/locale"):
                self.as_sudo("update-locale %s" % locale)
                self.run_command("exit")

        self.as_sudo("apt-get update -y -q")

        AptTask().run("nginx libjpeg-dev python-dev python-setuptools git-core "
                         "postgresql libpq-dev memcached supervisor")

        self.as_sudo("easy_install pip")
        self.as_sudo("pip install virtualenv mercurial")