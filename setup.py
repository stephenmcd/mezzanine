
from setuptools import setup, find_packages
import os

exclude = [
    "mezzanine/project_template/mezzanine.db",
    "mezzanine/project_template/local_settings.py",
]
exclude = dict([(e, None) for e in exclude])
for e in exclude:
    if e.endswith(".py"):
        try:
            os.remove("%sc" % e)
        except:
            pass
    try:
        with open(e, "r") as f:
            exclude[e] = (f.read(), os.stat(e))
        os.remove(e)
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
            "filebrowser_safe",
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
    for e in exclude:
        if exclude[e] is not None:
            data, stat = exclude[e]
            try:
                with open(e, "w") as f:
                    f.write(data)
                os.chown(e, stat.st_uid, stat.st_gid)
                os.chmod(e, stat.st_mode)
            except:
                pass

