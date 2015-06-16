
import platform
import sys

import django
from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.color import supports_color
from django.db import connection
from django.http import Http404
from django.utils.termcolors import colorize
from django.views.static import serve

import mezzanine


class MezzStaticFilesHandler(StaticFilesHandler):

    def _should_handle(self, path):
        return path.startswith((settings.STATIC_URL, settings.MEDIA_URL))

    def get_response(self, request):
        response = super(MezzStaticFilesHandler, self).get_response(request)
        if response.status_code == 404:
            locations = (
                (settings.STATIC_URL, settings.STATIC_ROOT),
                (settings.MEDIA_URL, settings.MEDIA_ROOT),
            )
            for url, root in locations:
                if request.path.startswith(url):
                    path = request.path.replace(url, "", 1)
                    try:
                        return serve(request, path, document_root=root)
                    except Http404:
                        # Just return the original 404 response.
                        pass
        return response


def banner():

    # Database name - this is just the ``vendor`` atrribute of
    # the connection backend, with some exceptions where we
    # replace it with something else, such as microsoft -> sql server.
    conn = connection
    db_name = {
        "microsoft": "sql server",
    }.get(conn.vendor, conn.vendor)
    db_name = "%s%s" % (db_name[:1].upper(),
        db_name.replace("sql", "SQL").replace("db", "DB")[1:])

    # Database version - vendor names mapped to functions that
    # retrieve the version, which should be a sequence of things
    # to join with dots.
    db_version_func = {
        "postgresql": lambda: (
            conn.pg_version // 10000,
            conn.pg_version // 100 % 100,
            conn.pg_version % 100,
        ),
        "mysql": lambda: conn.mysql_version,
        "sqlite": lambda: conn.Database.sqlite_version_info,
        # The remaining backends haven't actually been tested,
        # and so their version logic has been gleaned from glancing
        # at the code for each backend.
        "oracle": lambda: [conn.oracle_version],
        "microsoft": lambda: [conn._DatabaseWrapper__get_dbms_version()],
        "firebird": lambda: conn.server_version.split(" ")[-1].split("."),
    }.get(conn.vendor, lambda: [])
    db_version = ".".join(map(str, db_version_func()))

    # The raw banner split into lines.
    lines = ("""

              .....
          _d^^^^^^^^^b_
       .d''           ``b.
     .p'                `q.
    .d'                   `b.
   .d'                     `b.   * Mezzanine %(mezzanine_version)s
   ::                       ::   * Django %(django_version)s
  ::    M E Z Z A N I N E    ::  * Python %(python_version)s
   ::                       ::   * %(db_name)s %(db_version)s
   `p.                     .q'   * %(os_name)s %(os_version)s
    `p.                   .q'
     `b.                 .d'
       `q..          ..p'
          ^q........p^
              ''''


""" % {
        "mezzanine_version": mezzanine.__version__,
        "django_version": django.get_version(),
        "python_version": sys.version.split(" ", 1)[0],
        "db_name": db_name,
        "db_version": db_version,
        "os_name": platform.system(),
        "os_version": platform.release(),
    }).splitlines()[2:]

    if not supports_color():
        return "\n".join(lines)

    # Pairs of function / colorize args for coloring the banner.
    # These are each of the states moving from left to right on
    # a single line of the banner. The function represents whether
    # the current char in a line should trigger the next state.
    color_states = [
        (lambda c: c != " ", {}),
        (lambda c: c == " ", {"fg": "red"}),
        (lambda c: c != " " and not c.isupper(),
            {"fg": "white", "bg": "red", "opts": ["bold"]}),
        (lambda c: c == " ", {"fg": "red"}),
        (lambda c: c == "*", {}),
        (lambda c: c != "*", {"fg": "red"}),
        (lambda c: False, {}),
    ]

    # Colorize the banner.
    for i, line in enumerate(lines):
        chars = []
        color_state = 0
        for char in line:
            color_state += color_states[color_state][0](char)
            chars.append(colorize(char, **color_states[color_state][1]))
        lines[i] = "".join(chars)

    return "\n".join(lines)


class Command(runserver.Command):
    """
    Overrides runserver so that we can serve uploaded files
    during development, and not require every single developer on
    every single one of their projects to have to set up multiple
    web server aliases for serving static content.
    See https://code.djangoproject.com/ticket/15199

    For ease, we also serve any static files that have been stored
    under the project's ``STATIC_ROOT``.
    """

    def inner_run(self, *args, **kwargs):
        # Show Mezzanine's own cool banner in the terminal. There
        # aren't really any exceptions to catch here, but we do
        # so blanketly since such a trivial thing like the banner
        # shouldn't be able to crash the development server.
        try:
            self.stdout.write(banner())
        except:
            pass
        super(Command, self).inner_run(*args, **kwargs)

    def get_handler(self, *args, **options):
        handler = super(Command, self).get_handler(*args, **options)
        if settings.DEBUG or options["insecure_serving"]:
            handler = MezzStaticFilesHandler(handler)
        return handler
