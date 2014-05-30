from .abstract_server import AbstractServerTask


class RunTask(AbstractServerTask):
    """
    Runs a shell comand on the remote server.
    """
    name = "run"

    def run(self, command, show=True):
        return self.run_command(command, show)