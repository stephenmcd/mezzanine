from django import db
from django.core.management.base import BaseCommand

from mezzanine.twitter.models import Query, TwitterQueryException


class Command(BaseCommand):
    """
    Polls the Twitter API for tweets associated to the queries in templates.
    """

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    def handle(self, **options):
        queries = Query.objects.all()
        if not options["force"]:
            queries = queries.filter(interested=True)
        for query in queries:
            try:
                query.run()
            except TwitterQueryException as e:
                print(f"Twitter query error [{query}]: {e}")
        try:
            db.close_connection()
        except:  # noqa
            pass
