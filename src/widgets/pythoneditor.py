from PyQt4.QtCore import pyqtProperty
from PyQt4.Qsci import QsciLexerPython
from .commonscintilla import CommonScintilla


class PythonEditor(CommonScintilla):
    def __init__(self, parent):
        CommonScintilla.__init__(self, parent)
        # don't show the symbol margin
        self.setMarginWidth(1, 0)

        self.setLexer(QsciLexerPython())

    def getUser(self):
        return self.text()

    def setUser(self, value):
        self.setText(value)

    user = pyqtProperty(str, getUser, setUser, user=True)
