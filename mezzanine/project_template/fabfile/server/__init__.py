from fabric.api import env

from .run import RunTask
from .sudo import SudoTask
from .apt import AptTask
from .install import InstallTask


run_instance = RunTask()
sudo_instance = SudoTask()
apt_instance = AptTask()
install_instance = InstallTask(env)