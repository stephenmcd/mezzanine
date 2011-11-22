
from mezzanine.core.management.commands import createdb


class Command(createdb.Command):

    def handle_noargs(self, **options):
        from warnings import warn
        warn("install is deprecated; use: ./manage.py createdb")
        super(Command, self).handle_noargs(**options)
