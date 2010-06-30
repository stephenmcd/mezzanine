#!/usr/bin/env python

import os
import shutil
import sys

import mezzanine


class ProjectException(Exception):
    pass
    
def create_project():
    """
    Copies the contents of the project_template directory to a new directory 
    specified as an argument to the command line.
    """

    # Ensure a directory name is specified.
    script_name = os.path.basename(sys.argv[0])
    if len(sys.argv) == 1:
        raise ProjectException("Usage: %s project_name" % script_name)

    # Ensure the given directory name doesn't clash with an existing Python 
    # package/module.
    try:
        __import__(sys.argv[1])
    except ImportError:
        pass
    else:
        raise ProjectException("'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project name. Please try "
            "another name." % sys.argv[1])
                    
    mezzanine_path = os.path.dirname(os.path.abspath(mezzanine.__file__))
    from_path = os.path.join(mezzanine_path, "project_template")
    to_path = os.path.join(os.getcwd(), sys.argv[1])
    shutil.copytree(from_path, to_path)
        
if __name__ == "__main__":
    try:
        create_project()
    except ProjectException, e:
        print
        print e
        print
        


