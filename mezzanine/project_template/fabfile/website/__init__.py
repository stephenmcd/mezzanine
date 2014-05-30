from fabric.api import env

from .restart import RestartTask
from .manage import ManageTask
from .python import PythonTask


restart_instance = RestartTask(env)
manage_instance = ManageTask(env)
python_instance = PythonTask(env)
