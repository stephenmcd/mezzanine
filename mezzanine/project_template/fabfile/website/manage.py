from .abstract_website import AbstractWebsiteTask


class ManageTask(AbstractWebsiteTask):
    """
    Runs a Django management command.
    """
    name = "manage"

    def run(self, command):
        return self.run_command("%s %s" % (self.env.manage, command))