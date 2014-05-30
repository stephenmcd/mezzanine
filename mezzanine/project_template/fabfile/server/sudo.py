from .run import RunTask


class SudoTask(RunTask):
    """
    Runs a command as sudo.
    """
    name = "sudo"

    def run(self, command, show=True):
        return self.as_sudo(command, show)