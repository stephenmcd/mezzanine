
import os

from uuid import uuid4
# Generate a unique SECRET_KEY for the project's local_setttings module.
    #settings_path = os.path.join(os.getcwd(), project_name, "local_settings.py")
    settings_path = os.getcwd()
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        make_key = lambda: "%s%s%s" % (uuid4(), uuid4(), uuid4())
        data = data.replace("%(SECRET_KEY)s", make_key())
        data = data.replace("%(NEVERCACHE_KEY)s", make_key())
        f.write(data)