from fabric.api import env

from .run import RunTask
from .sudo import SudoTask
from .apt import AptTask
from .install import InstallTask


run_instance = RunTask(env)
sudo_instance = SudoTask(env)
apt_instance = AptTask(env)
install_instance = InstallTask(env)
