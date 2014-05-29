from .abstract_db import AbstractDatabaseTask


class BackupTask(AbstractDatabaseTask):
    """
    Backs up the database.
    """
    name = "backup"

    def run(self, filename):
        return self.postgres("pg_dump -Fc %s > %s" % (self.env.proj_name, filename))