from fabric.api import env

from .backup import BackupTask
from .psql import PsqlTask
from .restore import RestoreTask


backup_instance = BackupTask(env)
psql_instance = PsqlTask(env)
restore_instance = RestoreTask(env)
