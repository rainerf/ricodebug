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
from math import log, ceil
import logging

from PyQt4.QtGui import QPixmap, QFont, QFrame, QHBoxLayout, QLayout, QColor, QMenu
from PyQt4.QtCore import Qt, QFileSystemWatcher, QTimer, pyqtSignal, QPoint, QIODevice, QFile
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP, QsciStyle

from views.overlays import BreakpointOverlayWidget
from widgets.commonscintilla import CommonScintilla
from lib import formlayout
from helpers.tools import mixColor


class ScintillaWrapper(CommonScintilla):
    """
    A wrapper around QsciScintilla:
    * Only emits dwellStart events if the mouse is really dwelling over the
      widget and not somewhere else. Also, it provides an unfiltered but
      matching dwellEnd signal.
    * Allows overlaying inline widgets.
    """
    dwellStart = pyqtSignal(int, int, int)
    dwellEnd = pyqtSignal(int, int, int)

    def __init__(self, parent):
        CommonScintilla.__init__(self, parent)
        self.__mouseInWidget = False
        self.__overlayWidgets = {}

        self.SCN_DWELLSTART.connect(self.__dwellStartEvent)
        self.SCN_DWELLEND.connect(lambda pos, x, y: self.dwellEnd.emit(pos, x, y))
        self.SCN_MARGINCLICK.connect(self.updateOverlayPositions)

    def ensureLineVisible(self, *args, **kwargs):
        ret = QsciScintilla.ensureLineVisible(self, *args, **kwargs)
        self.updateOverlayPositions()
        return ret

    def updateOverlayPositions(self):
        for line in range(0, self.SendScintilla(QsciScintilla.SCI_GETLINECOUNT)):
            if self.SendScintilla(QsciScintilla.SCI_GETLINEVISIBLE, line):
                if line in self.__overlayWidgets:
                    overlay = self.__overlayWidgets[line]
                    self.__moveOverlayToLine(overlay, line)
                    overlay.show()
            else:
                if line in self.__overlayWidgets:
                    self.__overlayWidgets[line].hide()

    def enterEvent(self, event):
        self.__mouseInWidget = True
        return QsciScintilla.enterEvent(self, event)

    def leaveEvent(self, event):
        self.__mouseInWidget = False
        return QsciScintilla.leaveEvent(self, event)

    def __dwellStartEvent(self, pos, x, y):
        if self.__mouseInWidget:
            self.dwellStart.emit(pos, x, y)

    def __moveOverlayToLine(self, overlay, line):
        pos = self.positionFromLineIndex(int(line), 0)
        y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, pos)
        overlay.move(overlay.x(), y)

    def addOverlayWidget(self, w, line, col=None, offset=0, minX=0):
        line -= 1

        if line not in self.__overlayWidgets:
            cont = QFrame()
            cont.setStyleSheet("QFrame { background-color : transparent; }")
            cont.setLayout(QHBoxLayout())
            cont.layout().setSpacing(20)
            cont.layout().setMargin(0)
            cont.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
            cont.setParent(self.viewport())

            if col is None:
                col = self.lineLength(line) - 1
            else:
                col = min(col, self.lineLength(line) - 1)

            self.__moveOverlayToLine(cont, line)
            pos = self.positionFromLineIndex(int(line), col)
            x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, pos)
            cont.move(max(x + offset, minX), cont.y())

            cont.resize(10, self.textHeight(line))
            cont.show()

            self.__overlayWidgets[line] = cont

        w.setParent(self.__overlayWidgets[line])
        w.resize(w.size().width(), self.textHeight(line))
        self.__overlayWidgets[line].layout().addWidget(w)

    def removeOverlayWidget(self, w, line):
        line -= 1

        if not line in self.__overlayWidgets:
            # don't panic if the user requests to remove a non-existing overlay
            return

        self.__overlayWidgets[line].layout().removeWidget(w)
        w.setParent(None)
        self.__relayoutOverlay(self.__overlayWidgets[line])

    def __relayoutOverlay(self, overlay):
        overlay.layout().activate()
        overlay.resize(overlay.layout().minimumSize())

    def removeAllOverlayWidgets(self):
        for line, cont in self.__overlayWidgets.items():
            # remove all overlays from the container
            while True:
                w = self.__overlayWidgets[line].layout().takeAt(0)
                if not w:
                    break

            # remove the container itself
            cont.setParent(None)
        self.__overlayWidgets = {}

    def scrollContentsBy(self, dx, dy):
        for w in iter(self.__overlayWidgets.values()):
            # simply assume that all lines are of equal height
            p = w.pos() + QPoint(dx, dy * self.textHeight(0))
            w.move(p)

        return QsciScintilla.scrollContentsBy(self, dx, dy)


class OpenedFileView(ScintillaWrapper):
    MARGIN_NUMBERS, MARGIN_MARKER_FOLD, MARGIN_MARKER_BP, MARGIN_MARKER_TP, MARGIN_MARKER_EXEC, \
    MARGIN_MARKER_EXEC_SIGNAL, MARKER_HIGHLIGHTED_LINE, MARGIN_MARKER_STACK, MARGIN_MARKER_BP_DIS = range(9)

    def __init__(self, distributedObjects, filename, parent):
        ScintillaWrapper.__init__(self, parent)
        self.breakpointOverlays = {}

        filename = str(filename)
        self.distributedObjects = distributedObjects
        self.debugController = self.distributedObjects.debugController
        self.__bpModel = self.distributedObjects.breakpointModel
        self.tracepointController = self.distributedObjects.tracepointController
        self.signalProxy = self.distributedObjects.signalProxy
        self.filename = filename
        self.lastContextMenuLine = 0
        self.markerBp = QPixmap(":/markers/bp.png")
        self.markerBpDisabled = QPixmap(":/markers/bp_dis.png")
        self.markerTp = QPixmap(":/markers/tp.png")
        self.markerExec = QPixmap(":/markers/exec_pos.png")
        self.markerStack = QPixmap(":/markers/stack_pos.png")
        self.markerExecSignal = QPixmap(":/markers/exec_pos_signal.png")
        self.shown = False

        self.setToolTip("")
        self.setWhatsThis("")
        self.setMarginLineNumbers(self.MARGIN_NUMBERS, True)
        # set sensitivity
        self.setMarginSensitivity(self.MARGIN_NUMBERS, True)
        self.setMarginSensitivity(self.MARGIN_MARKER_BP, True)
        self.setMarginSensitivity(self.MARGIN_MARKER_TP, True)
        # define symbol
        self.markerDefine(self.markerBp, self.MARGIN_MARKER_BP)
        self.markerDefine(self.markerBpDisabled, self.MARGIN_MARKER_BP_DIS)
        self.markerDefine(self.markerTp, self.MARGIN_MARKER_TP)
        self.markerDefine(self.markerExec, self.MARGIN_MARKER_EXEC)
        self.markerDefine(self.markerStack, self.MARGIN_MARKER_STACK)
        self.markerDefine(self.markerExecSignal, self.MARGIN_MARKER_EXEC_SIGNAL)
        self.markerDefine(QsciScintilla.Background, self.MARKER_HIGHLIGHTED_LINE)

        # define width and mask to show margin
        self.setMarginWidth(self.MARGIN_MARKER_BP, 10)
        self.setMarginMarkerMask(self.MARGIN_MARKER_BP, 1 << self.MARGIN_MARKER_BP | 1 << self.MARGIN_MARKER_BP_DIS)
        self.setMarginWidth(self.MARGIN_MARKER_TP, 10)
        self.setMarginMarkerMask(self.MARGIN_MARKER_TP, 1 << self.MARGIN_MARKER_TP)
        self.setMarginWidth(self.MARGIN_MARKER_EXEC, 10)
        self.setMarginMarkerMask(self.MARGIN_MARKER_EXEC,
                1 << self.MARGIN_MARKER_EXEC |
                1 << self.MARGIN_MARKER_EXEC_SIGNAL |
                1 << self.MARGIN_MARKER_STACK)
        self.setMarginWidth(self.MARKER_HIGHLIGHTED_LINE, 0)
        self.setMarginMarkerMask(self.MARKER_HIGHLIGHTED_LINE, 1 << self.MARKER_HIGHLIGHTED_LINE)

        self.INDICATOR_TOOLTIP = self.indicatorDefine(self.BoxIndicator)
        self.setIndicatorDrawUnder(True, self.INDICATOR_TOOLTIP)

        self.setReadOnly(False)
        self.modificationChanged.connect(self.__setFileModified)

        self.SendScintilla(QsciScintilla.SCI_SETMOUSEDWELLTIME, 500)

        # override scintillas context menu with our own
        self.SendScintilla(QsciScintilla.SCI_USEPOPUP, 0)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.marginClicked.connect(self.onMarginClicked)
        self.SCN_DOUBLECLICK.connect(self.editDoubleClicked)
        self.dwellStart.connect(self.onDwellStart)
        self.dwellEnd.connect(self.onDwellEnd)

        self.__bpModel.rowsInserted.connect(self.breakpointsInserted)
        # don't connect to rowsRemoved here since the breakpoint is already gone
        # from the model when it's emitted
        self.__bpModel.rowsAboutToBeRemoved.connect(self.breakpointsRemoved)
        self.__bpModel.dataChanged.connect(self.breakpointsModified)
        _model = self.tracepointController.model()
        _model.rowsInserted.connect(self.getTracepointsFromModel)
        _model.rowsRemoved.connect(self.getTracepointsFromModel)

        act = self.distributedObjects.actions
        act.ToggleTrace.triggered.connect(self.toggleTracepoint)

        self.__allowToolTip = True
        self.__enableToolTip(True)

        self.__popupMenu = None

        self.__disAsmStyle = QsciStyle()

        self.__fileWatcher = QFileSystemWatcher([self.filename])
        self.__fileWatcher.fileChanged.connect(self.__fileChanged)

        # this timer is used for a workaround: QFileSystemWatcher will sometimes
        # report a change multiple times; therefore, in self.__fileChanged, we
        # simply start the timer on a notification and discard all notifications
        # while the timer is running
        self.__fileChangedTimer = QTimer()
        self.__fileChangedTimer.setSingleShot(True)
        self.__fileChangedTimer.setInterval(100)

        self.__wordHighlightTimer = QTimer()
        self.cursorPositionChanged.connect(lambda: self.__wordHighlightTimer.start())
        self.__wordHighlightTimer.setSingleShot(True)
        self.__wordHighlightTimer.setInterval(250)
        self.__wordHighlightTimer.timeout.connect(self.highlightWordFromCursorPosition)

        ScintillaWrapper.init(self, distributedObjects)
        self.setLexer(QsciLexerCPP())

        self.openFile()

    def updateConfig(self):
        if not ScintillaWrapper.updateConfig(self):
            return False
        # check whether we're supposed to use overlays and reload everything
        # that uses them
        qs = QsciScintilla
        c = self.distributedObjects.editorController.config
        l = self.lexer()
        self.setFolding(qs.BoxedTreeFoldStyle if c.folding.value else qs.NoFoldStyle, self.MARGIN_MARKER_FOLD)
        self.setMarkerBackgroundColor(QColor(c.highlightColor.value), self.MARKER_HIGHLIGHTED_LINE)
        l.setColor(QColor(c.preprocessorColor.value), l.PreProcessor)
        l.setColor(QColor(c.commentColor.value), l.CommentLine)
        l.setColor(QColor(c.commentColor.value), l.CommentDoc)

        self.__disAsmStyle.setFont(formlayout.tuple_to_qfont(self.distributedObjects.editorController.config.font.value))
        # make the annotation's background slightly shaded with the identifier color
        bg = QColor(self.distributedObjects.editorController.config.backgroundColor.value)
        fg = QColor(self.distributedObjects.editorController.config.identifierColor.value)
        self.__disAsmStyle.setPaper(mixColor(bg, .8, fg))
        self.__disAsmStyle.setColor(fg)

        self.__useBreakpointOverlays = c.useBreakpointOverlays.value
        self.getBreakpointsFromModel()
        self.setDisassemble(self.distributedObjects.editorController.config.showDisassemble.value)

        return True

    def __fileChanged(self):
        if not self.__fileChangedTimer.isActive():
            logging.warning("Source file %s modified. Recompile executable for correct debugging.", self.filename)
            self.__fileChangedTimer.start()

    def saveFile(self):
        ''' Save source file '''
        if (QFile.exists(self.filename)):
            f = open(self.filename, 'w')
            f.write(self.text())
            f.close()
            self.openFile()

    def openFile(self):
        if not (QFile.exists(self.filename)):
            logging.error("Could not open file %s", self.filename)

        self.file_ = QFile(self.filename)
        self.file_.open(QIODevice.ReadOnly | QIODevice.Text)
        self.read(self.file_)
        self.file_.close()
        self.setMarginWidthByLineNumbers()
        self.__setFileModified(False)

        # read all breakpoints and tracepoints from the model
        self.getTracepointsFromModel()
        self.getBreakpointsFromModel()

    def __setFileModified(self, modified):
        ''' Method called whenever current file is marked as modified '''
        self.distributedObjects.signalProxy.fileModified.emit(self.filename, modified)

    def onDwellStart(self, pos, x, y):
        if self.__allowToolTip:
            exp, (line, start, end) = self.getWordOrSelectionAndRangeFromPosition(pos)

            # try evaluating the expression before doing anything else: this will return None if the
            # expression is not valid (ie. something that is not a variable)
            if self.debugController.evaluateExpression(exp.strip()) is not None:
                startPos = self.positionFromLineIndex(line, start)
                x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, startPos)
                y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, startPos)
                self.distributedObjects.toolTipController.showToolTip(exp, QPoint(x + 3, y + 3 + self.textHeight(line)), self)

    def onDwellEnd(self, _1, _2, _3):
        self.distributedObjects.toolTipController.hideToolTip()

    def showContextMenu(self, point):
        scipos = self.SendScintilla(
                QsciScintilla.SCI_POSITIONFROMPOINT, point.x(), point.y())
        point = self.mapToGlobal(point)
        exp, (line, start, end) = self.getWordOrSelectionAndRangeFromPosition(scipos)

        # self.lineIndexFromPosition(..) returns tuple. first element is line
        self.lastContextMenuLine = int(self.lineIndexFromPosition(scipos)[0])

        self.__popupMenu = QMenu(self)
        self.__popupMenu.addAction(self.distributedObjects.actions.ToggleTrace)

        if exp:
            self.__popupMenu.addAction(self.distributedObjects.actions.getAddToWatchAction(exp, self.signalProxy.addWatch))
            self.__popupMenu.addAction(self.distributedObjects.actions.getAddToDatagraphAction(exp, self.distributedObjects.datagraphController.addWatch))
            self.__popupMenu.addAction(self.distributedObjects.actions.getAddWatchpointAction(exp, self.distributedObjects.breakpointModel.insertWatchpoint))

            listOfTracepoints = self.tracepointController.getTracepointsFromModel()
            if listOfTracepoints:
                subPopupMenu = QMenu(self)
                subPopupMenu.setTitle("Add variable " + exp + " to tracepoint...")

                for tp in listOfTracepoints:
                    subPopupMenu.addAction(self.distributedObjects.actions.getAddToTracepointAction(exp, tp.name, tp.addVar))

                self.__popupMenu.addSeparator()
                self.__popupMenu.addMenu(subPopupMenu)

        self.__popupMenu.popup(point)

        # disable the tooltips while the menu is shown
        self.__enableToolTip(False)
        self.__popupMenu.aboutToHide.connect(lambda: self.__enableToolTip(True))

    def __enableToolTip(self, enable):
        self.__allowToolTip = enable

    def isPositionInsideSelection(self, position):
        lf, cf, lt, ct = self.getSelection()
        pl, pc = self.lineIndexFromPosition(position)

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
            line, start, lineTo, end = self.getSelection()
            if line != lineTo:
                return "", (None, None, None)
        else:
            line, start, end = self.getWordRangeFromPosition(position)
        return self.getWordFromRange(line, start, end), (line, start, end)

    def getWordRangeFromPosition(self, position):
        line, col = self.lineIndexFromPosition(position)
        start, end = self.getWordRangeFromLineCol(line, col)
        return line, start, end

    def getWordRangeFromLineCol(self, line, col):
        s = str(self.text(line))
        start = col - 1
        end = col

        a = 0

        while start >= 0:
            if s[start].isalnum() or s[start] in [".", "_"]:
                pass
            elif s[start] == ">" and start >= 1 and s[start - 1] == "-":
                start -= 1
            elif s[start] == "]":
                a -= 1
            elif s[start] == "[":
                a += 1
            else:
                break
            start -= 1
        start += 1

        while end < len(s):
            if a >= 0:
                pass
            if s[end].isalnum() or s[end] == "_":
                pass
            elif s[end] == "]":
                a -= 1
            else:
                break
            end += 1

        if a == 0:
            return start, end
        else:
            return 0, 0

    def getWordFromLineCol(self, line, col):
        self.clearIndicatorRange(0, 0, self.lines(), 1, self.INDICATOR_TOOLTIP)

        start, end = self.getWordRangeFromLineCol(line, col)
        word = self.getWordFromRange(line, start, end)
        if word:
            for i, line in enumerate(self.text().split('\n')):
                for match in re.finditer(r"\b%s\b" % word, line):
                    self.fillIndicatorRange(i, match.start(), i, match.end(), self.INDICATOR_TOOLTIP)


    def getWordFromRange(self, line, start, end):
        return str(self.text(line))[start:end]

    def editDoubleClicked(self, position, line, modifiers):
        line, start, end = self.getWordRangeFromPosition(position)
        w = str(self.text(line))[start:end]
        if w:
            self.signalProxy.addWatch(w)

    def showExecutionPosition(self, line):
        self.markerAdd(line, self.MARGIN_MARKER_EXEC)
        self.showLine(line)

    def showSignalPosition(self, line):
        self.markerAdd(line, self.MARGIN_MARKER_EXEC_SIGNAL)
        self.showLine(line)

    def showLine(self, line):
        self.setCursorPosition(line, 1)
        self.ensureLineVisible(line)

    def clearExecutionPositionMarkers(self):
        self.markerDeleteAll(self.MARGIN_MARKER_EXEC)

    def setMarginWidthByLineNumbers(self):
        self.setMarginWidth(0, ceil(log(self.lines(), 10)) * 10 + 5)

    def onMarginClicked(self, margin, line, _):
        # if breakpoint should be toggled
        if margin == self.MARGIN_NUMBERS or margin == self.MARGIN_MARKER_BP:
            self.toggleBreakpointWithLine(line)
        elif margin == self.MARGIN_MARKER_TP:
            self.toggleTracepointWithLine(line)

    def highlightWordFromCursorPosition(self):
        line, col = self.getCursorPosition()

    def toggleBreakpointWithLine(self, line):
        self.__bpModel.toggleBreakpoint(self.filename, line + 1)

    def toggleTracepointWithLine(self, line):
        self.tracepointController.toggleTracepoint(self.filename, line + 1)

    def toggleTracepoint(self):
        self.toggleTracepointWithLine(self.lastContextMenuLine)

    def getBreakpointsFromModel(self):
        self.markerDeleteAll(self.MARGIN_MARKER_BP)
        self.markerDeleteAll(self.MARGIN_MARKER_BP_DIS)

        self.removeAllOverlayWidgets()
        self.breakpointOverlays = {}

        for bp in self.__bpModel.breakpoints:
            if bp.fullname == self.filename:
                self.markerAdd(bp.line - 1, self.MARGIN_MARKER_BP if bp.enabled else self.MARGIN_MARKER_BP_DIS)
                self.__addBreakpointOverlay(bp)

    def __addBreakpointOverlay(self, bp):
        if not self.__useBreakpointOverlays:
            return

        l = BreakpointOverlayWidget(self.viewport(), self.distributedObjects, bp, self.__bpModel)
        self.breakpointOverlays[bp.number] = l
        self.__updateBreakpointOverlay(bp)
        l.show()
        self.addOverlayWidget(l, int(bp.line), None, 50, 400)

    def __updateBreakpointOverlay(self, bp):
        if not self.__useBreakpointOverlays:
            return

        w = self.breakpointOverlays[bp.number]
        w.update()

    def __removeBreakpointOverlay(self, bp):
        if not self.__useBreakpointOverlays:
            return

        self.removeOverlayWidget(self.breakpointOverlays[bp.number], bp.line)

    def __validBreakpoints(self, startRow, endRow):
        for i in range(startRow, endRow + 1):
            # the column has no meaning here, all columns will return the
            # breakpoint object for role InternalDataRole
            bp = self.__bpModel.data(self.__bpModel.index(i, 0), self.__bpModel.InternalDataRole)
            if not bp.fullname == self.filename:
                continue
            yield bp

    def breakpointsInserted(self, _, start, end):
        for bp in self.__validBreakpoints(start, end):
            self.markerAdd(bp.line - 1, self.MARGIN_MARKER_BP if bp.enabled else self.MARGIN_MARKER_BP_DIS)
            self.__addBreakpointOverlay(bp)

    def breakpointsRemoved(self, _, start, end):
        for bp in self.__validBreakpoints(start, end):
            self.markerDelete(bp.line - 1, self.MARGIN_MARKER_BP)
            self.markerDelete(bp.line - 1, self.MARGIN_MARKER_BP_DIS)
            self.__removeBreakpointOverlay(bp)

    def breakpointsModified(self, topLeft, bottomRight):
        for bp in self.__validBreakpoints(topLeft.row(), bottomRight.row()):
            self.markerDelete(bp.line - 1, self.MARGIN_MARKER_BP)
            self.markerDelete(bp.line - 1, self.MARGIN_MARKER_BP_DIS)
            self.markerAdd(bp.line - 1, self.MARGIN_MARKER_BP if bp.enabled else self.MARGIN_MARKER_BP_DIS)
            self.__updateBreakpointOverlay(bp)

    def getTracepointsFromModel(self):
        """Get tracepoints from model."""
        self.markerDeleteAll(self.MARGIN_MARKER_TP)
        for tp in self.tracepointController.getTracepointsFromModel():
            if tp.fullname == self.filename:
                self.markerAdd(int(tp.line) - 1, self.MARGIN_MARKER_TP)

    def highlightLine(self, line):
        self.removeHighlightedLines()
        self.markerAdd(line, self.MARKER_HIGHLIGHTED_LINE)
        QTimer.singleShot(int(self.distributedObjects.editorController.config.highlightingDuration.value), self.removeHighlightedLines)

    def removeHighlightedLines(self):
        self.markerDeleteAll(self.MARKER_HIGHLIGHTED_LINE)

    def setDisassemble(self, enable):
        self.clearAnnotations()

        if not enable:
            return

        ret = self.distributedObjects.gdb_connector.disassemble(self.filename)

        for i in ret.asm_insns:
            assert i.dest=="src_and_asm_line"
            insns = "\n".join((j.address + " "*4 + j.inst for j in i.src.line_asm_insn))
            if insns:
                self.annotate(int(i.src.line)-1, insns, self.__disAsmStyle)
