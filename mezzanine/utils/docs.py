"""
Utils called from project_root/docs/conf.py when Sphinx
documentation is generated.
"""
import os.path
from shutil import copyfile, move
from socket import gethostname
from warnings import warn

from django.core.management import call_command
from django.template.defaultfilters import urlize
from django.utils.encoding import force_str
from django.utils.functional import Promise

from mezzanine.conf import registry
from mezzanine.utils.importing import import_dotted_path


def deep_force_unicode(value):
    """
    Recursively call force_str on value.
    """
    if isinstance(value, (list, tuple, set)):
        value = type(value)(map(deep_force_unicode, value))
    elif isinstance(value, dict):
        value = type(value)(map(deep_force_unicode, value.items()))
    elif isinstance(value, Promise):
        value = force_str(value)
    return value


def build_settings_docs(docs_path, prefix=None):
    """
    Converts names, descriptions and defaults for settings in
    ``mezzanine.conf.registry`` into RST format for use in docs,
    optionally filtered by setting names with the given prefix.
    """
    # String to use instead of setting value for dynamic defaults
    dynamic = "[dynamic]"
    lines = [".. THIS DOCUMENT IS AUTO GENERATED VIA conf.py"]
    for name in sorted(registry.keys()):
        if prefix and not name.startswith(prefix):
            continue
        setting = registry[name]
        settings_name = "``%s``" % name
        settings_label = ".. _%s:" % name
        setting_default = setting["default"]
        if isinstance(setting_default, str):
            if gethostname() in setting_default or (
                setting_default.startswith("/") and os.path.exists(setting_default)
            ):
                setting_default = dynamic
        if setting_default != dynamic:
            setting_default = repr(deep_force_unicode(setting_default))
        lines.extend(["", settings_label])
        lines.extend(["", settings_name, "-" * len(settings_name)])
        lines.extend(
            [
                "",
                urlize(setting["description"] or "")
                .replace('<a href="', "`")
                .replace('" rel="nofollow">', " <")
                .replace("</a>", ">`_"),
            ]
        )
        if setting["choices"]:
            choices = ", ".join(
                f"{str(v)}: ``{force_str(k)}``" for k, v in setting["choices"]
            )
            lines.extend(["", "Choices: %s" % choices, ""])
        lines.extend(["", "Default: ``%s``" % setting_default])
    with open(os.path.join(docs_path, "settings.rst"), "w") as f:
        f.write(
            "\n".join(lines)
            .replace("u'", "'")
            .replace("yo'", "you'")
            .replace("&#39;", "'")
            .replace("&#x27;", "'")
        )


def build_modelgraph(docs_path, package_name="mezzanine"):
    """
    Creates a diagram of all the models for mezzanine and the given
    package name, generates a smaller version and add it to the
    docs directory for use in model-graph.rst
    """
    to_path = os.path.join(docs_path, "img", "graph.png")
    build_path = os.path.join(docs_path, "build", "_images")
    resized_path = os.path.join(os.path.dirname(to_path), "graph-small.png")
    settings = import_dotted_path(
        package_name + ".project_template.project_name.settings"
    )
    apps = [
        a.rsplit(".")[1]
        for a in settings.INSTALLED_APPS
        if a.startswith("mezzanine.") or a.startswith(package_name + ".")
    ]
    try:
        call_command(
            "graph_models",
            *apps,
            inheritance=True,
            outputfile="graph.png",
            layout="dot",
        )
    except Exception as e:
        warn("Couldn't build model_graph, graph_models failed on: %s" % e)
    else:
        try:
            move("graph.png", to_path)
        except OSError as e:
            warn("Couldn't build model_graph, move failed on: %s" % e)
    # docs/img/graph.png should exist in the repo - move it to the build path.
    try:
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        copyfile(to_path, os.path.join(build_path, "graph.png"))
    except OSError as e:
        warn("Couldn't build model_graph, copy to build failed on: %s" % e)
    try:
        from PIL import Image

        with Image.open(to_path) as image:
            width = 800
            height = image.size[1] * 800 // image.size[0]
            image.resize((width, height))
            image.save(resized_path, "PNG", quality=100)
    except Exception as e:
        warn("Couldn't build model_graph, resize failed on: %s" % e)
    # Copy the dashboard screenshot to the build dir too. This doesn't
    # really belong anywhere, so we do it here since this is the only
    # spot we deal with doc images.
    d = "dashboard.png"
    copyfile(os.path.join(docs_path, "img", d), os.path.join(build_path, d))
