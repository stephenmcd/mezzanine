
from __future__ import with_statement
import os


requirements = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "project_template", "requirements", "project.txt")

with open(requirements) as f:
    for line in f:
        if line.startswith("Mezzanine=="):
            __version__ = line.split("==")[-1].strip()
