from .abstract_server import AbstractServerTask


class AptTask(AbstractServerTask):
    """
    Installs one or more system packages via apt.
    """
    name = "apt"

    def run(self, packages):
        self.as_sudo("apt-get install -y -q " + packages)