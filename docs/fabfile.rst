  * ``fab all`` - Installs everything required on a new system and deploy.
  * ``fab apt`` - Installs one or more system packages via apt.
  * ``fab backup`` - Backs up the project database.
  * ``fab create`` - Creates the environment needed to host the project.
  * ``fab deploy`` - Deploy latest version of the project.
  * ``fab install`` - Installs the base system and Python requirements for the entire server.
  * ``fab manage`` - Runs a Django management command.
  * ``fab pip`` - Installs one or more Python packages within the virtual environment.
  * ``fab psql`` - Runs SQL against the project's database.
  * ``fab python`` - Runs Python code in the project's virtual environment, with Django loaded.
  * ``fab remove`` - Blow away the current project.
  * ``fab restart`` - Restart gunicorn worker processes for the project.
  * ``fab restore`` - Restores the project database from a previous backup.
  * ``fab rollback`` - Reverts project state to the last deploy.
  * ``fab run`` - Runs a shell comand on the remote server.
  * ``fab secure`` - Minimal security steps for brand new servers.
  * ``fab sudo`` - Runs a command as sudo on the remote server.
