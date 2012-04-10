

class FileSystemEncodingChanged(RuntimeError):
    def __init__(self):
        msg = ("Access was attempted on a file that was saved to a "
               "filesystem with utf-8 support, but somehow the locale "
               "has changed and the filesystem does not support utf-8. "
               "You may need to set 'LC_CTYPE' to a correct value via "
               "your terminal, eg: 'en_US.utf8'.")
        RuntimeError.__init__(self, msg)
