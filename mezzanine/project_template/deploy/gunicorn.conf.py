import os

bind = "127.0.0.1:%(gunicorn_port)s"
workers = (os.sysconf("SC_NPROCESSORS_ONLN") * 2) + 1
loglevel = "error"
proc_name = "%(proj_name)s"
