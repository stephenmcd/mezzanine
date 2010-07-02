#!/usr/bin/env python

import os
import sys
import shutil
import mezzanine

def create_project():
    script_name = os.path.basename(sys.argv[0])
    if len(sys.argv) != 2:
        usage(script_name)
        sys.exit()

    project_name = sys.argv[1]

    # stops creating '-foo' directories when user incorrectly is trying to
    #   give the script an --option.
    if project_name.startswith("-"):
        usage(script_name)
        sys.exit()

        
    mezzanine_path = os.path.dirname(os.path.abspath(mezzanine.__file__))
    from_path = os.path.join(mezzanine_path, "project_template")
    to_path = os.path.join(os.getcwd(), project_name)

    try:
        shutil.copytree(from_path, to_path)
    except Exception, e:
        print
        print "Error in %s: %s" % (script_name, e)
        print

def usage(script_name):
    print
    print "Usage: %s project_name" % script_name
    print
        
if __name__ == "__main__":
    create_project()
