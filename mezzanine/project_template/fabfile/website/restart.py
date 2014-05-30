from fabric.contrib.files import exists

from .abstract_website import AbstractWebsiteTask


class RestartTask(AbstractWebsiteTask):
    """
    Restart gunicorn worker processes for the project.
    """
    name = "restart"

    def run(self):
        pid_path = "%s/gunicorn.pid" % self.env.proj_path
        if exists(pid_path):
            self.as_sudo("kill -HUP `cat %s`" % pid_path)
        else:
            start_args = (self.env.proj_name, self.env.proj_name)
            self.as_sudo("supervisorctl start %s:gunicorn_%s" % start_args)