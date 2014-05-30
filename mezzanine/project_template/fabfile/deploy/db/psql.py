from .abstract_db import AbstractDatabaseTask


class PsqlTask(AbstractDatabaseTask):
    """
    Runs SQL against the project's database.
    """
    name = "psql"

    def run(self, sql, show=True):
        out = self.postgres('psql -c "%s"' % sql)
        if show:
            self.print_command(sql)
        return out