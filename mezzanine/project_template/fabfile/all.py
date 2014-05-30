from .mezzanine import MezzanineTask
from deploy import CreateTask, DeployTask
from server import InstallTask


class AllTask(MezzanineTask):
    """
    Installs everything required on a new system and deploy.
    From the base software, up to the deployed project.
    """
    name = "all"

    def run(self):
        InstallTask(self.env).run()
        if CreateTask(self.env).run():
            DeployTask(self.env).run()