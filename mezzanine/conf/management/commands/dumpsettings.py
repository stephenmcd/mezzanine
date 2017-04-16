from __future__ import unicode_literals

from builtins import str as text
from collections import defaultdict

import sys
import textwrap

from django.core.management.base import BaseCommand
from django.utils.functional import Promise

from mezzanine.conf import registry


PREFIX = "# "
INDENT = 4
LINE_LENGTH = 80 - len(PREFIX)


def pretty_format(value, indent=4, depth=0):
    """ Pretty format a value depending on type """

    def format_collection(value, delimiters="[]", depth=0):
        """ Format a list, or tuple, or dict in a human friendly way """

        start_delimiter, end_delimiter = delimiters
        newline = "\n" + PREFIX

        items_output = ""
        items_line = ""

        for item in value:
            # Format each item in the collection and add it to the total output
            new_item = pretty_format(item, indent=indent, depth=depth + 1)
            new_item += ", "

            # Start to calculate max line length at this depth
            length = indent * (depth + 1) + len(items_line)

            # Check if the formatted item has newlines
            first_newline = new_item.find("\n")
            multi_line = first_newline >= 0

            # If item contains newlines, up to the first one counts for length
            length += first_newline if multi_line else len(new_item)

            if length > LINE_LENGTH:
                # If items_line has content already then we can't add anymore
                if items_line:
                    items_output += items_line[:-1]  # Remove trailing space
                else:
                    raise RuntimeError(
                        "Line is too big to break: %s" % new_item)

                # Add a newline and set next item as the start of the new line
                items_output += newline
                items_line = new_item
            else:
                # Continue the current line, there's still room for now
                items_line += new_item

        # We're out of items so add what's left as the last item
        items_output += items_line[:-2]  # Remove trailing comma and space

        # If the content between the delimiters has newlines then we indent it
        multi_line = items_output.count("\n") > 0

        # Format the collection either all on one line, or indented across many
        output = start_delimiter
        if multi_line:
            # Start content on a new line and indent it properly
            output += newline
            output += " " * indent
            output += items_output.replace(newline, newline + " " * indent)
        else:
            output += items_output
        if multi_line:
            output += newline  # End delimiter is on its own line, not indented
        output += end_delimiter

        return output

    # Convert the value to a suitable format to output to a Python file
    if value is None:
        output = str(value)
    elif isinstance(value, list):
        output = format_collection(value, delimiters="[]", depth=depth)
    elif isinstance(value, tuple):
        output = format_collection(value, delimiters="()", depth=depth)
    elif isinstance(value, dict):
        output = format_collection(value, delimiters="{}", depth=depth)
    elif isinstance(value, bool):
        output = str(value)
    elif isinstance(value, int) or isinstance(value, float):
        output = str(value)
    elif isinstance(value, text):
        output = '"%s"' % value
    elif isinstance(value, Promise):
        output = '_("%s")' % value.encode("utf-8")
    else:
        raise TypeError("Unknown setting type")

    return output


class Command(BaseCommand):
    help = "Dump the registered settings for this project."

    option_list = BaseCommand.option_list
    args = ""

    def handle(self, *args, **options):
        app_settings = defaultdict(list)

        for setting in registry.values():
            app_prefix = setting["app"].split(".")[0]
            app_settings[app_prefix].append(setting)

        # Let's include some imports so that it's a working settings file
        sys.stdout.write(
            "from __future__ import absolute_import, unicode_literals\n\n")
        sys.stdout.write(
            "from django.utils.translation import ugettext_lazy as _\n\n")

        # Sort everything to get Mezzanine first, then loop through the apps
        sorted_apps = sorted(app_settings, key=lambda app: app != "mezzanine")
        for idx, app_prefix in enumerate(sorted_apps):
            header = "# %s SETTINGS #" % app_prefix.upper()

            if idx:
                sys.stdout.write("\n\n")

            # Output a nice text block header
            sys.stdout.write("#" * len(header) + "\n")
            sys.stdout.write(header + "\n")
            sys.stdout.write("#" * len(header) + "\n")

            # Output each setting in the app
            for setting in app_settings[app_prefix]:
                name = setting["name"]
                description = (setting["description"] or "").encode("utf-8")

                # TODO - If default is None, we'd like to put something, maybe
                #        add an example keyword arg to ``register_setting``?
                default = pretty_format(setting["default"], indent=INDENT)
                value = name + " = " + default

                # Not all commands have a description, but if they do make it
                # it pretty by line wrapping it and
                if description:
                    pretty_description = "\n".join(textwrap.wrap(
                        description, initial_indent="# ",
                        subsequent_indent="# ", width=78)
                    )
                    sys.stdout.write("\n" + pretty_description)

                sys.stdout.write("\n")

                # Find the first newline in the setting name & value output
                newline = value.find("\n")
                end = len(value) if newline < 0 else newline

                # If the first line would go past 80 characters, use a slash
                # to continue it on the next line, indented accordingly
                if end > LINE_LENGTH:
                    sys.stdout.write(PREFIX + name + " = \\\n")
                    sys.stdout.write(PREFIX + " " * INDENT + default + "\n")
                else:
                    sys.stdout.write(PREFIX + value + "\n")
