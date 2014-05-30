from fabric.contrib.files import exists

from .abstract_deploy import AbstractDeployTask
from .db import PsqlTask


class RemoveTask(AbstractDeployTask):
    """
    Blow away the current project.
    """
    name = "remove"

    def run(self):
        if exists(self.env.venv_path):
            self.as_sudo("rm -rf %s" % self.env.venv_path)
        for template in self.get_templates().values():
            remote_path = template["remote_path"]
            if exists(remote_path):
                self.as_sudo("rm %s" % remote_path)
        psql_task = PsqlTask(self.env)
        psql_task.run("DROP DATABASE IF EXISTS %s;" % self.env.proj_name)
        psql_task.run("DROP USER IF EXISTS %s;" % self.env.proj_name)