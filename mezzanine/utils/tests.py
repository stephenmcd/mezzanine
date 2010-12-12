
from __future__ import with_statement
from compiler import parse
import os

from mezzanine.utils.path import path_for_import


# Ignore these warnings in pyflakes.
PYFLAKES_IGNORE = (
    "import *' used",
    "'memcache' imported but unused",
    "'cmemcache' imported but unused",
    "'__version__' imported but unused",
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
                compile(source, f, "exec")
            except (SyntaxError, IndentationError), value:
                info = (path, value.lineno, value.args[0])
                warnings.append("Invalid syntax in %s:%d: %s" % info)
            result = Checker(parse(source), path)
            for warning in result.messages:
                message = unicode(warning)
                for ignore in ignore_strings:
                    if ignore in message:
                        break
                else:
                    warnings.append(message)
    return warnings
