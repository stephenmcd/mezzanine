from posixpath import join

from fabric.api import cd

from .abstract_deploy import AbstractDeployTask
from .db import RestoreTask
from ..website import RestartTask


class RollbackTask(AbstractDeployTask):
    """
    Reverts project state to the last deploy.
    When a deploy is performed, the current state of the project is
    backed up. This includes the last commit checked out, the database,
    and all static files. Calling rollback will revert all of these to
    their state prior to the last deploy.
    """
    name = "rollback"

    def run(self):
        with self.project():
            with self.update_changed_requirements():
                update = "git checkout" if self.env.git else "hg up -C"
                self.run_command("%s `cat last.commit`" % update)
            with cd(join(self.static(), "..")):
                self.run_command("tar -xf %s" % join(self.env.proj_path, "last.tar"))
            RestoreTask(self.env).run("last.db")
        RestartTask(self.env).run()