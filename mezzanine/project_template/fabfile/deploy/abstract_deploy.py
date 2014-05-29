import os
import re
from getpass import getpass
from contextlib import contextmanager
from posixpath import join

from fabric.api import hide, cd, prefix
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from ..mezzanine import MezzanineTask
from ..website import PythonTask
from .pip import PipTask


class AbstractDeployTask(MezzanineTask):
    """
    Abstract class for common utils used for managing deployment
    """

    def __init__(self, environment, templates, *args, **kwargs):
        super(MezzanineTask, self).__init__(*args, **kwargs)

        self.env = environment
        self.templates = templates

    @contextmanager
    def update_changed_requirements(self):
        """
        Checks for changes in the requirements file across an update,
        and gets new requirements if changes have occurred.
        """
        reqs_path = join(self.env.proj_path, self.env.reqs_path)
        get_reqs = lambda: self.run_command("cat %s" % reqs_path, show=False)
        old_reqs = get_reqs() if self.env.reqs_path else ""
        yield
        if old_reqs:
            new_reqs = get_reqs()
            if old_reqs == new_reqs:
                # Unpinned requirements should always be checked.
                for req in new_reqs.split("\n"):
                    if req.startswith("-e"):
                        if "@" not in req:
                            # Editable requirement without pinned commit.
                            break
                    elif req.strip() and not req.startswith("#"):
                        if not set(">=<") & set(req):
                            # PyPI requirement without version.
                            break
                else:
                    # All requirements are pinned.
                    return
            PipTask(self.env).run("-r %s/%s" % (self.env.proj_path, self.env.reqs_path))

    def db_pass(self):
        """
        Prompts for the database password if unknown.
        """
        if not self.env.db_pass:
            self.env.db_pass = getpass("Enter the database password: ")
        return self.env.db_pass

    def get_templates(self):
        """
        Returns each of the templates with env vars injected.
        """
        injected = {}
        for name, data in self.templates.items():
            injected[name] = dict([(k, v % self.env) for k, v in data.items()])
        return injected

    def static(self):
        """
        Returns the live STATIC_ROOT directory.
        """
        return PythonTask(self.env).run_command("from django.conf import settings;"
                                                "print settings.STATIC_ROOT", show=False).split("\n")[-1]

    def upload_template_and_reload(self, name):
        """
        Uploads a template only if it has changed, and if so, reload a
        related service.
        """
        template = self.get_templates()[name]
        local_path = template["local_path"]
        if not os.path.exists(local_path):
            project_root = os.path.dirname(os.path.abspath(__file__))
            local_path = os.path.join(project_root, local_path)
        remote_path = template["remote_path"]
        reload_command = template.get("reload_command")
        owner = template.get("owner")
        mode = template.get("mode")
        remote_data = ""
        if exists(remote_path):
            with hide("stdout"):
                remote_data = self.as_sudo("cat %s" % remote_path, show=False)
        with open(local_path, "r") as f:
            local_data = f.read()
            # Escape all non-string-formatting-placeholder occurrences of '%':
            local_data = re.sub(r"%(?!\(\w+\)s)", "%%", local_data)
            if "%(db_pass)s" in local_data:
                self.env.db_pass = self.db_pass()
            local_data %= self.env
        clean = lambda s: s.replace("\n", "").replace("\r", "").strip()
        if clean(remote_data) == clean(local_data):
            return
        upload_template(local_path, remote_path, self.env, use_sudo=True, backup=False)
        if owner:
            self.as_sudo("chown %s %s" % (owner, remote_path))
        if mode:
            self.as_sudo("chmod %s %s" % (mode, remote_path))
        if reload_command:
            self.as_sudo(reload_command)