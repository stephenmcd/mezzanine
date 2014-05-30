from .abstract_deploy import MezzanineTask


class PipTask(MezzanineTask):
    """
    Installs one or more Python packages within the virtual environment.
    """
    name = "pip"

    def run(self, packages):
        with self.virtualenv():
            return self.as_sudo("pip install %s" % packages)