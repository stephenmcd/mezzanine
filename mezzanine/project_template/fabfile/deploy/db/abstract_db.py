from ..abstract_deploy import AbstractDeployTask


class AbstractDatabaseTask(AbstractDeployTask):
    def postgres(self, command):
        """
        Runs the given command as the postgres user.
        """
        show = not command.startswith("psql")
        return self.run_command("sudo -u root sudo -u postgres %s" % command, show=show)