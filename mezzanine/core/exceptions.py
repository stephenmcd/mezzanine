

class FileSystemEncodingChanged(RuntimeError):
    def __init__(self):
        msg = ("Access was attempted on a file that contains unicode "
               "characters in its path, but somehow the current locale "
               "does not support utf-8. You may need to set 'LC_ALL' "
               "to a correct value, eg: 'en_US.UTF-8'.")
        RuntimeError.__init__(self, msg)
