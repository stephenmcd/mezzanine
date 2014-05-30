from fabric.contrib.files import exists
from future.builtins import input

from .db import BackupTask
from .create import CreateTask
from .abstract_deploy import AbstractDeployTask
from ..website import RestartTask, ManageTask


class DeployTask(AbstractDeployTask):
    """
    Deploy latest version of the project.
    Check out the latest version of the project from version
    control, install new requirements, sync and migrate the database,
    collect any new static assets, and restart gunicorn's work
    processes for the project.
    """
    name = "deploy"

    def run(self):
        if not exists(self.env.venv_path):
            prompt = input("\nVirtualenv doesn't exist: %s"
                           "\nWould you like to create it? (yes/no) "
                           % self.env.proj_name)
            if prompt.lower() != "yes":
                print("\nAborting!")
                return False
            CreateTask(self.env).run()
        for name in self.get_templates():
            self.upload_template_and_reload(name)
        with self.project():
            BackupTask(self.env).run("last.db")
            static_dir = self.static()
            if exists(static_dir):
                self.run_command("tar -cf last.tar %s" % static_dir)
            git = self.env.git
            last_commit = "git rev-parse HEAD" if git else "hg id -i"
            self.run_command("%s > last.commit" % last_commit)
            with self.update_changed_requirements():
                if git:
                    self.run_command("git pull origin master -f")
                else:
                    self.run_command("hg pull && hg up -C")
            manage_task = ManageTask(self.env)
            manage_task.run("collectstatic -v 0 --noinput")
            manage_task.run("syncdb --noinput")
            manage_task.run("migrate --noinput")
        RestartTask(self.env).run()
        return True