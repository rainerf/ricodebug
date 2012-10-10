# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# This file is part of ricodebug.
#
# ricodebug is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information see <http://syscdbg.hagenberg.servus.at/>.

import re
from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.QtGui import QPixmap, QFont, QColor
from PyQt4.QtCore import QObject, Qt, QFileSystemWatcher, QTimer
from math import log, ceil
import logging


class OpenedFileView(QObject):
    MARGIN_NUMBERS, MARGIN_MARKER_FOLD, MARGIN_MARKER_BP, MARGIN_MARKER_TP, MARGIN_MARKER_EXEC, \
    MARGIN_MARKER_EXEC_SIGNAL, MARKER_HIGHLIGHTED_LINE, MARGIN_MARKER_STACK = range(8)

    def __init__(self, distributedObjects, filename, parent):
        QObject.__init__(self, parent)
        filename = str(filename)
        self.distributedObjects = distributedObjects
        self.debugController = self.distributedObjects.debugController
        self.breakpointController = self.distributedObjects.breakpointController
        self.tracepointController = self.distributedObjects.tracepointController
        self.signalProxy = self.distributedObjects.signalProxy
        self.filename = filename
        self.lastContexMenuLine = 0
        self.markerBp = QPixmap(":/markers/bp.png")
        self.markerTp = QPixmap(":/markers/tp.png")
        self.markerExec = QPixmap(":/markers/exec_pos.png")
        self.markerStack = QPixmap(":/markers/stack_pos.png")
        self.markerExecSignal = QPixmap(":/markers/exec_pos_signal.png")
        self.shown = False

        self.FileWatcher = QFileSystemWatcher()
        self.FileWatcher.addPath(self.filename)
        self.FileWatcher.fileChanged.connect(self.fileChanged)

        self.tab = QtGui.QWidget()
        self.gridLayout = QtGui.QGridLayout(self.tab)
        self.gridLayout.setMargin(0)
        self.edit = Qsci.QsciScintilla(self.tab)
        self.font = QFont("DejaVu Sans Mono", 10)
        self.font.setStyleHint(QFont.TypeWriter)
        self.lexer = Qsci.QsciLexerCPP()
        self.lexer.setFont(self.font)

        self.edit.setToolTip("")
        self.edit.setWhatsThis("")
        self.edit.setLexer(self.lexer)
        self.edit.setMarginLineNumbers(self.MARGIN_NUMBERS, True)
        # set sensitivity
        self.edit.setMarginSensitivity(self.MARGIN_NUMBERS, True)
        self.edit.setMarginSensitivity(self.MARGIN_MARKER_BP, True)
        self.edit.setMarginSensitivity(self.MARGIN_MARKER_TP, True)
        # define symbol
        self.edit.markerDefine(self.markerBp, self.MARGIN_MARKER_BP)
        self.edit.markerDefine(self.markerTp, self.MARGIN_MARKER_TP)
        self.edit.markerDefine(self.markerExec, self.MARGIN_MARKER_EXEC)
        self.edit.markerDefine(self.markerStack, self.MARGIN_MARKER_STACK)
        self.edit.markerDefine(self.markerExecSignal, self.MARGIN_MARKER_EXEC_SIGNAL)
        self.edit.markerDefine(Qsci.QsciScintilla.Background, self.MARKER_HIGHLIGHTED_LINE)
        # define width and mask to show margin
        self.edit.setMarginWidth(self.MARGIN_MARKER_BP, 10)
        self.edit.setMarginMarkerMask(self.MARGIN_MARKER_BP, 1 << self.MARGIN_MARKER_BP)
        self.edit.setMarginWidth(self.MARGIN_MARKER_TP, 10)
        self.edit.setMarginMarkerMask(self.MARGIN_MARKER_TP, 1 << self.MARGIN_MARKER_TP)
        self.edit.setMarginWidth(self.MARGIN_MARKER_EXEC, 10)
        self.edit.setMarginMarkerMask(self.MARGIN_MARKER_EXEC,
                1 << self.MARGIN_MARKER_EXEC |
                1 << self.MARGIN_MARKER_EXEC_SIGNAL |
                1 << self.MARGIN_MARKER_STACK)
        self.edit.setMarginWidth(self.MARKER_HIGHLIGHTED_LINE, 0)
        self.edit.setMarginMarkerMask(self.MARKER_HIGHLIGHTED_LINE, 1 << self.MARKER_HIGHLIGHTED_LINE)

        self.INDICATOR_TOOLTIP = self.edit.indicatorDefine(self.edit.BoxIndicator, -1)

        self.edit.setReadOnly(False)
        self.gridLayout.addWidget(self.edit, 0, 0, 1, 1)

        self.breakpoints = []

        if not (QtCore.QFile.exists(filename)):
            logging.error("could not open file", filename)
        self.file_ = QtCore.QFile(filename)
        self.file_.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        self.edit.read(self.file_)
        self.file_.close()

        self.changed = False
        self.edit.modificationChanged.connect(self.__setFileModified)

        self.setMarginWidthByLineNumbers()
        self.edit.SendScintilla(Qsci.QsciScintilla.SCI_SETMOUSEDWELLTIME, 500)

        # override scintillas context menu with our own
        self.edit.SendScintilla(Qsci.QsciScintilla.SCI_USEPOPUP, 0)
        self.edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.edit.customContextMenuRequested.connect(self.showContextMenu)

        self.edit.marginClicked.connect(self.marginClicked)
        self.edit.SCN_DOUBLECLICK.connect(self.editDoubleClicked)
        self.edit.SCN_DWELLSTART.connect(self.dwellStart)
        self.edit.SCN_DWELLEND.connect(self.dwellEnd)

        # initially, read all breakpoints and tracepoints from the model
        self.getBreakpointsFromModel()
        self.getTracepointsFromModel()

        _model = self.breakpointController.model()
        _model.rowsInserted.connect(self.getBreakpointsFromModel)
        _model.rowsRemoved.connect(self.getBreakpointsFromModel)
        _model = self.tracepointController.model()
        _model.rowsInserted.connect(self.getTracepointsFromModel)
        _model.rowsRemoved.connect(self.getTracepointsFromModel)

        act = self.distributedObjects.actions
        act.ToggleTrace.triggered.connect(self.toggleTracepoint)

        self.distributedObjects.editorController.config.itemsHaveChanged.connect(self.updateConfig)
        self.updateConfig()

        self.__allowToolTip = True
        self.__enableToolTip(True)

    def updateConfig(self):
        qs = Qsci.QsciScintilla
        c = self.distributedObjects.editorController.config
        self.edit.setWhitespaceVisibility(qs.WsVisible if c.showWhiteSpaces.value else qs.WsInvisible)
        self.edit.setIndentationGuides(c.showIndentationGuides.value)
        self.edit.setTabWidth(int(c.tabWidth.value))
        self.edit.setWrapMode(qs.WrapWord if c.wrapLines.value else qs.WrapNone)
        self.edit.setFolding(qs.BoxedTreeFoldStyle if c.folding.value else qs.NoFoldStyle, self.MARGIN_MARKER_FOLD)
        self.lexer.setPaper(QColor(c.backgroundColor.value))
        self.lexer.setColor(QColor(c.identifierColor.value), self.lexer.Identifier)
        self.lexer.setColor(QColor(c.identifierColor.value), self.lexer.Operator)
        self.edit.setCaretForegroundColor(QColor(c.identifierColor.value))
        self.lexer.setColor(QColor(c.keywordColor.value), self.lexer.Keyword)
        self.lexer.setColor(QColor(c.stringColor.value), self.lexer.SingleQuotedString)
        self.lexer.setColor(QColor(c.stringColor.value), self.lexer.DoubleQuotedString)
        self.lexer.setColor(QColor(c.numberColor.value), self.lexer.Number)
        self.lexer.setColor(QColor(c.preprocessorColor.value), self.lexer.PreProcessor)
        self.lexer.setColor(QColor(c.commentColor.value), self.lexer.Comment)
        self.lexer.setColor(QColor(c.commentColor.value), self.lexer.CommentLine)
        self.lexer.setColor(QColor(c.commentColor.value), self.lexer.CommentDoc)
        self.edit.setIndicatorForegroundColor(QColor(c.tooltipIndicatorColor.value))
        self.edit.setMarkerBackgroundColor(QColor(c.highlightColor.value), self.MARKER_HIGHLIGHTED_LINE)

    def fileChanged(self):
        logging.warning("Source file %s modified. Recompile executable for \
                correct debugging.", self.filename)

    def saveFile(self):
        ''' Save source file '''
        if (QtCore.QFile.exists(self.filename)):
            f = open(self.filename, 'w')
            f.write(self.edit.text())
            f.close()
            self.file_.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
            self.edit.read(self.file_)
            self.file_.close()
            self.__setFileModified(False)

    def __setFileModified(self, modified):
        ''' Method called whenever current file is marked as modified '''
        self.distributedObjects.signalProxy.emitFileModified(self.filename, modified)

    def dwellStart(self, pos, x, y):
        # check self.edit.hasFocus() since QScintilla will emit dwell events
        # even when not focused
        if self.edit.hasFocus() and self.__allowToolTip and self.edit.frameGeometry().contains(x, y):
            exp, (line, start, end) = self.getWordOrSelectionAndRangeFromPosition(pos)

            # try evaluating the expression before doing anything else: this will return None if the
            # expression is not valid (ie. something that is not a variable)
            if self.debugController.evaluateExpression(exp.strip()) is not None:
                self.edit.fillIndicatorRange(line, start, line, end, self.INDICATOR_TOOLTIP)
                startPos = self.edit.positionFromLineIndex(line, start)
                x = self.edit.SendScintilla(Qsci.QsciScintilla.SCI_POINTXFROMPOSITION, 0, startPos)
                y = self.edit.SendScintilla(Qsci.QsciScintilla.SCI_POINTYFROMPOSITION, 0, startPos)
                self.distributedObjects.toolTipController.showToolTip(exp, QtCore.QPoint(x + 3, y + 3 + self.edit.textHeight(line)), self.edit)

    def dwellEnd(self, position, x, y):
        self.distributedObjects.toolTipController.hideToolTip()
        self.edit.clearIndicatorRange(0, 0, self.edit.lines(), 1, self.INDICATOR_TOOLTIP)

    def showContextMenu(self, point):
        scipos = self.edit.SendScintilla(
                Qsci.QsciScintilla.SCI_POSITIONFROMPOINT, point.x(), point.y())
        point = self.edit.mapToGlobal(point)
        exp, (line, start, end) = self.getWordOrSelectionAndRangeFromPosition(scipos)
        self.edit.fillIndicatorRange(line, start, line, end, self.INDICATOR_TOOLTIP)

        # self.edit.lineIndexFromPosition(..) returns tuple. first element is line
        self.lastContexMenuLine = int(self.edit.lineIndexFromPosition(scipos)[0])

        listOfTracepoints = self.tracepointController.getTracepointsFromModel()

        self.subPopupMenu = QtGui.QMenu(self.edit)
        self.subPopupMenu.setTitle("Add variable " + exp + " to...")

        for tp in listOfTracepoints:
            self.subPopupMenu.addAction(self.distributedObjects.actions.getAddToTracepointAction(exp, tp.name, tp.addVar))

        self.popupMenu = QtGui.QMenu(self.edit)
        self.popupMenu.addAction(self.distributedObjects.actions.getAddToWatchAction(exp, self.signalProxy.addWatch))
        self.popupMenu.addAction(self.distributedObjects.actions.ToggleTrace)
        self.popupMenu.addAction(self.distributedObjects.actions.getAddToDatagraphAction(exp, self.distributedObjects.datagraphController.addWatch))
        self.popupMenu.addSeparator()
        self.popupMenu.addMenu(self.subPopupMenu)
        self.popupMenu.popup(point)

        # disable the tooltips while the menu is shown
        self.__enableToolTip(False)
        self.popupMenu.aboutToHide.connect(lambda: self.__enableToolTip(True))

    def __enableToolTip(self, enable):
        self.__allowToolTip = enable

    def isPositionInsideSelection(self, position):
        lf, cf, lt, ct = self.edit.getSelection()
        pl, pc = self.edit.lineIndexFromPosition(position)

        if lf < pl and pl < lt:
            return True
        elif lf == pl and pl < lt:
            return True if cf <= pc else False
        elif lf < pl and pl == lt:
            return True if pc <= ct else False
        elif lf == pl and pl == lt:
            return True if (cf <= pc and pc <= ct) else False
        else:
            return False

    def getWordOrSelectionAndRangeFromPosition(self, position):
        if self.isPositionInsideSelection(position):
            line, start, lineTo, end = self.edit.getSelection()
            if line != lineTo:
                return ""
        else:
            line, start, end = self.getWordRangeFromPosition(position)
        l = str(self.edit.text(line))
        return l[start:end], (line, start, end)

    def getWordRangeFromPosition(self, position):
        line, col = self.edit.lineIndexFromPosition(position)
        s = str(self.edit.text(line))
        start = col - 1
        end = col

        r = re.compile(r'[\w\d_\.]')    # FIXME: also scan over ->
        while start >= 0:
            if not r.match(s[start]):
                break
            start -= 1
        start += 1
        r = re.compile(r'[\w\d_]')
        while end < len(s):
            if not r.match(s[end]):
                break
            end += 1
        return (line, start, end)

    def editDoubleClicked(self, position, line, modifiers):
        line, start, end = self.getWordRangeFromPosition(position)
        l = str(self.edit.text(line))
        self.signalProxy.addWatch(str(l[start:end]))

    def showExecutionPosition(self, line):
        self.edit.markerAdd(line, self.MARGIN_MARKER_EXEC)
        self.showLine(line)

    def showSignalPosition(self, line):
        self.edit.markerAdd(line, self.MARGIN_MARKER_EXEC_SIGNAL)
        self.showLine(line)

    def showLine(self, line):
        self.edit.setCursorPosition(line, 1)
        self.edit.ensureLineVisible(line)

    def clearExecutionPositionMarkers(self):
        self.edit.markerDeleteAll(self.MARGIN_MARKER_EXEC)

    def setMarginWidthByLineNumbers(self):
        self.edit.setMarginWidth(0, ceil(log(self.edit.lines(), 10)) * 10 + 5)

    def marginClicked(self, margin, line, state):
        # if breakpoint should be toggled
        if margin == self.MARGIN_NUMBERS or margin == self.MARGIN_MARKER_BP:
            self.toggleBreakpointWithLine(line)
        elif margin == self.MARGIN_MARKER_TP:
            self.toggleTracepointWithLine(line)

    def toggleBreakpointWithLine(self, line):
        self.breakpointController.toggleBreakpoint(self.filename, line + 1)

    def toggleTracepointWithLine(self, line):
        self.tracepointController.toggleTracepoint(self.filename, line + 1)

    def toggleTracepoint(self):
        self.toggleTracepointWithLine(self.lastContexMenuLine)

    def getBreakpointsFromModel(self, parent=None, start=None, end=None):
        """Get breakpoints from model."""
        # TODO: don't reload all breakpoints, just the one referenced by parent/start/end
        self.edit.markerDeleteAll(self.MARGIN_MARKER_BP)
        for bp in self.breakpointController.getBreakpointsFromModel():
            if bp.fullname == self.filename:
                self.edit.markerAdd(int(bp.line) - 1, self.MARGIN_MARKER_BP)

    def getTracepointsFromModel(self):
        """Get tracepoints from model."""
        self.edit.markerDeleteAll(self.MARGIN_MARKER_TP)
        for tp in self.tracepointController.getTracepointsFromModel():
            if tp.fullname == self.filename:
                self.edit.markerAdd(int(tp.line) - 1, self.MARGIN_MARKER_TP)

    def highlightLine(self, line):
        self.removeHighlightedLines()
        self.edit.markerAdd(line, self.MARKER_HIGHLIGHTED_LINE)
        QTimer.singleShot(int(self.distributedObjects.editorController.config.highlightingDuration.value),
                          self.removeHighlightedLines)

    def removeHighlightedLines(self):
        self.edit.markerDeleteAll(self.MARKER_HIGHLIGHTED_LINE)
