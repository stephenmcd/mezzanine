
from __future__ import with_statement
from _ast import PyCF_ONLY_AST
import os

from mezzanine.utils.importing import path_for_import


# Ignore these warnings in pyflakes - if added to, please comment why.
PYFLAKES_IGNORE = (
    "import *' used",                     # Required by Django's urlconf API.
    "'__version__' imported but unused",  # Used to version subpackages.
    "redefinition of unused 'Feed'",      # Compatibility for Django 1.3/1.4
    "redefinition of unused 'feed'",      # Compatibility for Django 1.3/1.4
    "redefinition of unused 'debug'",     # Compatibility for Django <= 1.2
    "redefinition of unused 'info'",      # Compatibility for Django <= 1.2
    "redefinition of unused 'success'",   # Compatibility for Django <= 1.2
    "redefinition of unused 'warning'",   # Compatibility for Django <= 1.2
    "redefinition of unused 'error'",     # Compatibility for Django <= 1.2
)


def _run_checker_for_package(checker, package_name):
    """
    Runs the checker function across every Python module in the
    given package.
    """
    package_path = path_for_import(package_name)
    for (root, dirs, files) in os.walk(package_path):
        for f in files:
            # Ignore migrations.
            directory = root.split(os.sep)[-1]
            if (f == "local_settings.py" or not f.endswith(".py")
                or directory == "migrations"):
                continue
            for warning in checker(os.path.join(root, f)):
                yield warning.replace(package_path, package_name, 1)


def run_pyflakes_for_package(package_name, extra_ignore=None):
    """
    If pyflakes is installed, run it across the given package name
    returning any warnings found.
    """
    from pyflakes.checker import Checker
    ignore_strings = PYFLAKES_IGNORE
    if extra_ignore:
        ignore_strings += extra_ignore

    def pyflakes_checker(path):
        with open(path, "U") as source_file:
            source = source_file.read()
        try:
            tree = compile(source, path, "exec", PyCF_ONLY_AST)
        except (SyntaxError, IndentationError), value:
            info = (path, value.lineno, value.args[0])
            yield "Invalid syntax in %s:%d: %s" % info
        else:
            result = Checker(tree, path)
            for warning in result.messages:
                message = unicode(warning)
                for ignore in ignore_strings:
                    if ignore in message:
                        break
                else:
                    yield message

    return _run_checker_for_package(pyflakes_checker, package_name)


def run_pep8_for_package(package_name):
    """
    If pep8 is installed, run it across the given package name
    returning any warnings or errors found.
    """
    import pep8
    package_path = path_for_import(package_name)
    pep8.process_options(["-r", package_path])

    class Checker(pep8.Checker):
        """
        Subclass pep8's Checker to hook into error reporting.
        """

        def report_error(self, line_number, offset, text, check):
            """
            Store pairs of line numbers and errors.
            """
            self.errors.append((line_number, text.split(" ", 1)[1]))

        def check_all(self, *args, **kwargs):
            """
            Assign the errors attribute and return it after running.
            """
            self.errors = []
            super(Checker, self).check_all(*args, **kwargs)
            return self.errors

    def pep8_checker(path):
        for line_number, text in Checker(path).check_all():
            yield "%s:%s: %s" % (path, line_number, text)

    return _run_checker_for_package(pep8_checker, package_name)
