"""
Utils called from project_root/docs/conf.py when Sphinx
documentation is generated.
"""

from __future__ import with_statement
from datetime import datetime
import os.path
from shutil import copyfile, move
from socket import gethostname
from warnings import warn

from django.utils.datastructures import SortedDict
from PIL import Image

from mezzanine import __version__
from mezzanine.conf import registry
from mezzanine.utils.importing import import_dotted_path


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
            setting_default = repr(setting_default)
        lines.extend(["", settings_name, "-" * len(settings_name)])
        lines.extend(["", setting["description"].replace("<b>", "``"
            ).replace("</b>", "``").replace("<a href=\"", "`"
            ).replace("\" rel=\"nofollow\">", " <").replace("</a>", ">`_")])
        if setting["choices"]:
            choices = ", ".join(["%s: ``%s``" % (v, k) for k, v in
                                 setting["choices"]])
            lines.extend(["", "Choices: %s" % choices, ""])
        lines.extend(["", "Default: ``%s``" % setting_default])
    with open(os.path.join(docs_path, "settings.rst"), "w") as f:
        f.write("\n".join(lines))

# Python complains if this is inside build_changelog which uses exec.
_changeset_date = lambda c: datetime.fromtimestamp(c.date()[0])


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

    # Load the repo.
    try:
        from mercurial import ui, hg, error
    except ImportError:
        pass
    else:
        try:
            repo = hg.repository(ui.ui(), project_path)
        except error.RepoError:
            return
    if repo is None:
        return

    # Go through each changeset and assign it to the versions dict.
    changesets = [repo.changectx(changeset) for changeset in repo.changelog]
    for changeset in sorted(changesets, reverse=True, key=_changeset_date):
        # Check if the file with the version number is in this changeset
        # and if it is, pull it out and assign it as a variable.
        files = changeset.files()
        new_version = False
        if version_file in files:
            for line in changeset[version_file].data().split("\n"):
                if line.startswith(version_var):
                    exec line
                    if locals()[version_var] == "0.1.0":
                        locals()[version_var] = "1.0.0"
                        break
                    date = _changeset_date(changeset)
                    versions[locals()[version_var]] = {
                        "changes": [], "date": date.strftime("%b %d, %Y")}
                    new_version = len(files) == 1
        # Ignore changesets that are merges, bumped the version, closed
        # a branch or regenerated the changelog itself.
        merge = len(changeset.parents()) > 1
        branch_closed = len(files) == 0
        changelog_update = changelog_filename in files
        if merge or new_version or branch_closed or changelog_update:
            continue
        # Ensure we have a current version and if so, add this changeset's
        # description to it.
        try:
            version = locals()[version_var]
        except KeyError:
            continue
        else:
            description = changeset.description().rstrip(".").replace("\n", "")
            user = changeset.user().split("<")[0].strip()
            entry = "%s - %s" % (description, user)
            if entry not in versions[version]["changes"]:
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
