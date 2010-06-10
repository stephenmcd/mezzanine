
from setuptools import setup, find_packages
import os

db_file = "mezzanine/project_template/mezzanine.db"
db_data = None
try:
    with open("db_file", "r") as f:
        db_data = f.read()
    os.remove(db_file)
except:
    pass

try:
    setup(

        name = "Mezzanine",
        version = __import__("mezzanine").__version__,
        author = "Stephen McDonald",
        author_email = "stephen.mc@gmail.com",
        description = "A content management platform built using the Django framework.",
        long_description = open("README.rst").read(),
        license = "BSD",
        url = "http://github.com/stephenmcd/mezzanine/",
        zip_safe = False,
        include_package_data = True,
        packages = find_packages(),

        install_requires = [
            "setuptools",
            "grappelli_safe",
            "django-filebrowser",
            "PIL",
        ],

        entry_points = """
            [console_scripts]
            mezzanine-project=mezzanine.bin.mezzanine_project:create_project
        """,

        classifiers = [
            "Development Status :: 4 - Beta",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Internet :: WWW/HTTP :: WSGI",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]

    )
finally:
    if db_data is not None:
        try:
            with open(db_file, "w") as f:
                f.write(db_data)
        except:
            pass

