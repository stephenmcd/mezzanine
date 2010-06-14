#!/usr/bin/env python

"""
Converts the last backward-compatible filebrowser branch into a newly named 
package ``filebrowser_safe``.
"""

import os

branch_url = "http://django-filebrowser.googlecode.com/svn/branches/filebrowser_3"
package_name_from = branch_url.split("/")[-1]
package_name_to = "filebrowser_safe"

if not os.path.exists(package_name_from):
    print "Checking out branch..."
    os.system("svn co %s" % branch_url)

for (dirpath, dirnames, filenames) in os.walk(package_name_from, False):
    for name in dirnames:
        path = os.path.join(dirpath, name)
        # Delete SVN directories.
        if ".svn" in path:
            print "Deleting svn %s" % path
            os.rmdir(path)    for name in filenames:
        path = os.path.join(dirpath, name)
        # Delete SVN files.
        if ".svn" in path:
            print "Deleting svn %s" % path
            os.remove(path)
        elif path.endswith(".py"):
            update = False
            with open(path, "r") as f:
                data = f.read()
            if name == "admin.py":
                # Comment out calls to admin.site.register.
                update = True
                data = data.replace("\nadmin.site.register", 
                    "\n#admin.site.register")
            # Replace these instances of the package name with the new name.
            for replace_str in ("filebrowser.", "app_label = \"filebrowser\""):
                if replace_str in data:
                    update = True
                    data = data.replace(replace_str, 
                        replace_str.replace("filebrowser", package_name_to))
            if update:
                print "Rewriting %s" % path
                with open(path, "w") as f:
                    f.write(data)

# Move the package to the Mezzanine directory using the filebrowser_safe name.
script_path = os.path.dirname(os.path.abspath(__file__))
os.renames(package_name_from, os.path.join(script_path, "..", "..", 
    package_name_to))
