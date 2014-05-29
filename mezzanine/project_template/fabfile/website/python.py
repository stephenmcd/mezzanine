from .abstract_website import AbstractWebsiteTask
from posixpath import join


class PythonTask(AbstractWebsiteTask):
    """
    Runs Python code in the project's virtual environment, with Django loaded.
    """
    name = "python"

    def run(self, code, show=True):
        setup = "import os; os.environ[\'DJANGO_SETTINGS_MODULE\']=\'settings\';"
        full_code = 'python -c "%s%s"' % (setup, code.replace("`", "\\\`"))
        with self.project():
            result = self.run_command(full_code, show=False)
            if show:
                self.print_command(code)
        return result