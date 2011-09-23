
from __future__ import with_statement
from _ast import PyCF_ONLY_AST
import os

from mezzanine.utils.importing import path_for_import


# Ignore these warnings in pyflakes - if added to, please comment why.
PYFLAKES_IGNORE = (
    "import *' used", # Required by Django's urlconf API.
    "'__version__' imported but unused", # Used to version subpackages.
    "redefinition of unused 'Feed'", # Compatibility for Django 1.3/1.4
    "redefinition of unused 'feed'", # Compatibility for Django 1.3/1.4
)


def run_pyflakes_for_package(package_name, extra_ignore=None):
    """
    If pyflakes is installed, run it across the given package name
    returning any warnings found.
    """
    ignore_strings = PYFLAKES_IGNORE
    if extra_ignore:
        ignore_strings += extra_ignore
    try:
        from pyflakes.checker import Checker
    except ImportError:
        return []
    warnings = []
    for (root, dirs, files) in os.walk(path_for_import(package_name)):
        for f in files:
            # Ignore migrations.
            directory = root.split(os.sep)[-1]
            if not f.endswith(".py") or directory == "migrations":
                continue
            path = os.path.join(root, f)
            with open(path, "U") as source_file:
                source = source_file.read()
            try:
                tree = compile(source, f, "exec", PyCF_ONLY_AST)
            except (SyntaxError, IndentationError), value:
                info = (path, value.lineno, value.args[0])
                warnings.append("Invalid syntax in %s:%d: %s" % info)
                continue
            result = Checker(tree, path)
            for warning in result.messages:
                message = unicode(warning)
                for ignore in ignore_strings:
                    if ignore in message:
                        break
                else:
                    warnings.append(message)

    return warnings
