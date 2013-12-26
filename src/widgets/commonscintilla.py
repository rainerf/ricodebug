from PyQt4.Qsci import QsciScintilla
from PyQt4.QtGui import QFont, QColor
from lib import formlayout


class CommonScintilla(QsciScintilla):
    def __init__(self, parent):
        QsciScintilla.__init__(self, parent)
        self.__lexer = None
        self.__do = None

    def init(self, do):
        self.__do = do
        self.__do.editorController.config.itemsHaveChanged.connect(self.updateConfig)
        self.updateConfig()

    def setLexer(self, lexer):
        QsciScintilla.setLexer(self, lexer)
        # store the lexer locally to avoid garbage collection killing it
        self.__lexer = lexer
        self.updateConfig()

    def updateConfig(self):
        if not self.__lexer or not self.__do:
            return False

        qs = QsciScintilla
        c = self.__do.editorController.config
        self.setWhitespaceVisibility(qs.WsVisible if c.showWhiteSpaces.value else qs.WsInvisible)
        self.setIndentationGuides(c.showIndentationGuides.value)
        self.setTabWidth(int(c.tabWidth.value))
        self.setWrapMode(qs.WrapWord if c.wrapLines.value else qs.WrapNone)
        self.setBraceMatching(qs.SloppyBraceMatch if c.braceMatching.value else qs.NoBraceMatch)
        l = self.__lexer
        #font = QFont("DejaVu Sans Mono", 10)
        l.setFont(formlayout.tuple_to_qfont(c.font.value))
        l.setPaper(QColor(c.backgroundColor.value))
        l.setColor(QColor(c.identifierColor.value), l.Identifier)
        l.setColor(QColor(c.identifierColor.value), l.Operator)
        l.setColor(QColor(c.keywordColor.value), l.Keyword)
        l.setColor(QColor(c.stringColor.value), l.SingleQuotedString)
        l.setColor(QColor(c.stringColor.value), l.DoubleQuotedString)
        l.setColor(QColor(c.numberColor.value), l.Number)
        l.setColor(QColor(c.commentColor.value), l.Comment)
        self.setCaretForegroundColor(QColor(c.identifierColor.value))
        self.setIndicatorForegroundColor(QColor(c.tooltipIndicatorColor.value))

        return True
