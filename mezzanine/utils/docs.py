"""
Utils called from project_root/docs/conf.py when Sphinx
documentation is generated.
"""

from __future__ import with_statement
from datetime import datetime
import os.path
from shutil import copyfile, move
from string import letters
from socket import gethostname
from warnings import warn

from django.template.defaultfilters import urlize
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from PIL import Image

from mezzanine import __version__
from mezzanine.conf import registry
from mezzanine.utils.importing import import_dotted_path, path_for_import


def deep_force_unicode(value):
    """
    Recursively call force_unicode on value.
    """
    if isinstance(value, (list, tuple, set)):
        value = type(value)(map(deep_force_unicode, value))
    elif isinstance(value, dict):
        value = type(value)(map(deep_force_unicode, value.items()))
    elif isinstance(value, Promise):
        value = force_unicode(value)
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
        setting_default = setting["default"]
        if isinstance(setting_default, basestring):
            if gethostname() in setting_default or (
                setting_default.startswith("/") and
                os.path.exists(setting_default)):
                setting_default = dynamic
        if setting_default != dynamic:
            setting_default = repr(deep_force_unicode(setting_default))
        lines.extend(["", settings_name, "-" * len(settings_name)])
        lines.extend(["", urlize(setting["description"]
            ).replace("<a href=\"", "`"
            ).replace("\" rel=\"nofollow\">", " <").replace("</a>", ">`_")])
        if setting["choices"]:
            choices = ", ".join(["%s: ``%s``" % (unicode(v), force_unicode(k))
                                 for k, v in setting["choices"]])
            lines.extend(["", "Choices: %s" % choices, ""])
        lines.extend(["", "Default: ``%s``" % setting_default])
    with open(os.path.join(docs_path, "settings.rst"), "w") as f:
        f.write("\n".join(lines))


def build_deploy_docs(docs_path):
    try:
        from fabric.main import load_fabfile
    except ImportError:
        warn("Couldn't build fabfile.rst, fabric not installed")
        return
    project_template_path = path_for_import("mezzanine.project_template")
    commands = load_fabfile(os.path.join(project_template_path, "fabfile"))[1]
    lines = []
    for name in sorted(commands.keys()):
        doc = commands[name].__doc__.strip().split("\n")[0]
        lines.append("  * ``fab %s`` - %s" % (name, doc))
    with open(os.path.join(docs_path, "fabfile.rst"), "w") as f:
        f.write("\n".join(lines))


# Python complains if this is inside build_changelog which uses exec.
_changeset_date = lambda cs: datetime.fromtimestamp(cs.date()[0])


def build_changelog(docs_path, package_name="mezzanine"):
    """
    Converts Mercurial commits into a changelog in RST format.
    """

    project_path = os.path.join(docs_path, "..")
    version_file = os.path.join(package_name, "__init__.py")
    version_var = "__version__"
    changelog_filename = "CHANGELOG"
    changelog_file = os.path.join(project_path, changelog_filename)
    versions = SortedDict()
    repo = None
    ignore = ("AUTHORS", "formatting", "typo", "pep8", "pep 8",
              "whitespace", "README", "trans", "print debug",
              "debugging", "tabs", "style", "sites", "ignore",
              "tweak", "cleanup", "minor", "for changeset",
              ".com``", "oops", "syntax")
    hotfixes = {
        "40cbc47b8d8a": "1.0.9",
        "a25749986abc": "1.0.10",
    }

    # Load the repo.
    try:
        from mercurial import ui, hg, error
        from mercurial.commands import tag
    except ImportError:
        pass
    else:
        try:
            ui = ui.ui()
            repo = hg.repository(ui, project_path)
        except error.RepoError:
            return
    if repo is None:
        return

    # Go through each changeset and assign it to the versions dict.
    changesets = [repo.changectx(changeset) for changeset in repo.changelog]
    for cs in sorted(changesets, reverse=True, key=_changeset_date):
        # Check if the file with the version number is in this changeset
        # and if it is, pull it out and assign it as a variable.
        files = cs.files()
        new_version = False
        # Commit message cleanup hacks.
        description = cs.description().rstrip(".").replace("\n", ". ")
        while "  " in description:
            description = description.replace("  ", " ")
        description = description.replace(". . ", ". ").replace("...", ",")
        while ".." in description:
            description = description.replace("..", ".")
        description = description.replace(":.", ":").replace("n'. t", "n't")
        words = description.split()
        # Format var names in commit.
        for i, word in enumerate(words):
            if (set("._") & set(word[:-1]) and set(letters) & set(word)
                and "`" not in word and not word[0].isdigit()):
                last = ""
                if word[-1] in ",.":
                    last, word = word[-1], word[:-1]
                words[i] = "``%s``%s" % (word, last)
        description = " ".join(words)
        if version_file in files:
            for line in cs[version_file].data().split("\n"):
                if line.startswith(version_var):
                    exec line
                    if locals()[version_var] == "0.1.0":
                        locals()[version_var] = "1.0.0"
                        break
                    versions[locals()[version_var]] = {
                        "changes": [],
                        "date": _changeset_date(cs).strftime("%b %d, %Y")
                    }
                    new_version = len(files) == 1

        # Tag new versions.
        hotfix = hotfixes.get(cs.hex()[:12])
        if hotfix or new_version:
            if hotfix:
                version_tag = hotfix
            else:
                try:
                    version_tag = locals()[version_var]
                except KeyError:
                    version_tag = None
            if version_tag and version_tag not in cs.tags():
                print "Tagging version %s" % version_tag
                tag(ui, repo, version_tag, rev=cs.hex())

        # Ignore changesets that are merges, bumped the version, closed
        # a branch, regenerated the changelog itself, contain an ignore
        # word, or are one word long.
        merge = len(cs.parents()) > 1
        branch_closed = len(files) == 0
        changelog_update = changelog_filename in files
        ignored = [w for w in ignore if w.lower() in description.lower()]
        one_word = len(description.split()) == 1
        if (merge or new_version or branch_closed or changelog_update or
            ignored or one_word):
            continue
        # Ensure we have a current version and if so, add this changeset's
        # description to it.
        version = None
        try:
            version = locals()[version_var]
        except KeyError:
            if not hotfix:
                continue
        user = cs.user().split("<")[0].strip()
        entry = "%s - %s" % (description, user)
        if hotfix or entry not in versions[version]["changes"]:
            if hotfix:
                versions[hotfix] = {
                    "changes": [entry],
                    "date": _changeset_date(cs).strftime("%b %d, %Y"),
                }
            else:
                versions[version]["changes"].insert(0, entry)

    # Write out the changelog.
    with open(changelog_file, "w") as f:
        for version, version_info in versions.items():
            header = "Version %s (%s)" % (version, version_info["date"])
            f.write("%s\n" % header)
            f.write("%s\n" % ("-" * len(header)))
            f.write("\n")
            if version_info["changes"]:
                for change in version_info["changes"]:
                    f.write("  * %s\n" % change)
            else:
                f.write("  * No changes listed.\n")
            f.write("\n")


def build_modelgraph(docs_path, package_name="mezzanine"):
    """
    Creates a diagram of all the models for mezzanine and the given
    package name, generates a smaller version and add it to the
    docs directory for use in model-graph.rst
    """
    to_path = os.path.join(docs_path, "img", "graph.png")
    build_path = os.path.join(docs_path, "build", "_images")
    resized_path = os.path.join(os.path.dirname(to_path), "graph-small.png")
    settings = import_dotted_path(package_name + ".project_template.settings")
    apps = [a.rsplit(".")[1] for a in settings.INSTALLED_APPS
            if a.startswith("mezzanine.") or a.startswith(package_name + ".")]
    try:
        from django_extensions.management.commands import graph_models
    except ImportError:
        warn("Couldn't build model_graph, django_extensions not installed")
    else:
        options = {"inheritance": True, "outputfile": "graph.png",
                   "layout": "dot"}
        try:
            graph_models.Command().execute(*apps, **options)
        except Exception, e:
            warn("Couldn't build model_graph, graph_models failed on: %s" % e)
        else:
            try:
                move("graph.png", to_path)
            except OSError, e:
                warn("Couldn't build model_graph, move failed on: %s" % e)
    # docs/img/graph.png should exist in the repo - move it to the build path.
    try:
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        copyfile(to_path, os.path.join(build_path, "graph.png"))
    except OSError, e:
        warn("Couldn't build model_graph, copy to build failed on: %s" % e)
    try:
        image = Image.open(to_path)
        image.width = 800
        image.height = image.size[1] * 800 / image.size[0]
        image.save(resized_path, "PNG", quality=100)
    except Exception, e:
        warn("Couldn't build model_graph, resize failed on: %s" % e)
        return


def build_requirements(docs_path, package_name="mezzanine"):
    """
    Updates the requirements file with Mezzanine's version number.
    """
    mezz_string = "Mezzanine=="
    project_path = os.path.join(docs_path, "..")
    requirements_file = os.path.join(project_path, package_name,
                                     "project_template", "requirements",
                                     "project.txt")
    with open(requirements_file, "r") as f:
        requirements = f.readlines()
    with open(requirements_file, "w") as f:
        f.write("Mezzanine==%s\n" % __version__)
        for requirement in requirements:
            if requirement.strip() and not requirement.startswith(mezz_string):
                f.write(requirement)
