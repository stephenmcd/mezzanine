from fabric.api import env

from .deploy import DeployTask
from .create import CreateTask
from .pip import PipTask
from .remove import RemoveTask
from .rollback import RollbackTask
import db


deploy_instance = DeployTask(env)
create_instance = CreateTask(env)
pip_instance = PipTask(env)
remove_instance = RemoveTask(env)
rollback_instance = RollbackTask(env)
