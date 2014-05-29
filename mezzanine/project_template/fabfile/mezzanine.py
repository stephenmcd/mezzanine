from contextlib import contextmanager

from fabric.tasks import Task
from fabric.colors import yellow, blue, red
from fabric.api import run, hide, sudo, cd, prefix


class MezzanineTask(Task):
    @contextmanager
    def virtualenv(self):
        """
        Runs commands within the project's virtualenv.
        """
        with cd(self.env.venv_path):
            with prefix("source %s/bin/activate" % self.env.venv_path):
                yield

    @contextmanager
    def project(self):
        """
        Runs commands within the project's directory.
        """
        with self.virtualenv():
            with cd(self.env.proj_dirname):
                yield

    def _print(self, output):
        print()
        print(output)
        print()

    def print_command(self, command):
        self._print(blue("$ ", bold=True) +
                    yellow(command, bold=True) +
                    red(" ->", bold=True))

    def run_command(self, command, show=True):
        if show:
            self.print_command(command)
        with hide("running"):
            return run(command)

    def as_sudo(self, command, show=True):
        if show:
            self.print_command(command)
        with hide("running"):
            return sudo(command)

            #TODO: abstract the class