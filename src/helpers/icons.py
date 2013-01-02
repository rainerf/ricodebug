from PyQt4.QtGui import QIcon


class Icons:
    """
    @DynamicAttrs
    """
    icons = ["time", "locals", "gdb", "stack", "exclusive", "python", "thread", "console", "bp", "clear", "local", "tp", "watch", "files", "datagraph", "pause", "stop"]

    def __init__(self):
        for i in self.icons:
            setattr(self.__class__, i, QIcon(":/icons/images/%s.png" % i))