"""
Utils called from project_root/docs/conf.py when Sphinx 
documentation is generated. 
"""

from __future__ import with_statement
from datetime import datetime
import os.path
from socket import gethostname

from django.utils.datastructures import SortedDict

from mezzanine.conf import registry


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
        lines.extend(["", setting["description"]])
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
                    date = _changeset_date(changeset)
                    versions[locals()[version_var]] = {
                        "changes": [], "date": date.strftime("%b %d, %Y")}
                    new_version = len(files) == 1
        # Ignore changesets that are merges, bumped the version, closed 
        # a branch or regenerated the changelog itself.
        merge = len(changeset.parents()) > 1
        branch_closed = len(files) == 0
        changelog_update = changelog_filename in files and len(files) == 1
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
