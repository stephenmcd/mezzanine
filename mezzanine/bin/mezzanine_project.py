#!/usr/bin/env python

import os
import sys
import shutil
import mezzanine

def create_project():

    script_name = os.path.basename(sys.argv[0])
    if len(sys.argv) == 1:
        print
        print "Usage: %s project_name" % script_name
        print
        sys.exit()
        
    mezzanine_path = os.path.dirname(os.path.abspath(mezzanine.__file__))
    from_path = os.path.join(mezzanine_path, "project_template")
    to_path = os.path.join(os.getcwd(), sys.argv[1])

    try:
        shutil.copytree(from_path, to_path)
    except Exception, e:
        print
        print "Error in %s: %s" % (script_name, e)
        print
        
if __name__ == "__main__":
    create_project()
