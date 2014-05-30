from .abstract_db import AbstractDatabaseTask


class RestoreTask(AbstractDatabaseTask):
    """
    Restores the database.
    """

    def run(self, filename):
        return self.postgres(
            "pg_restore -c -d %s %s" % (self.env.proj_name, filename))