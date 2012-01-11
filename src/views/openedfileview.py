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

import re, cgi
from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.QtGui import QPixmap, QIcon, QToolTip, QFont, QColor
from PyQt4.QtCore import SIGNAL, QObject, Qt
from math import log, ceil
from actions import ActionEx, Actions
import logging

class OpenedFileView(QObject):
	MARGIN_NUMBERS, MARGIN_MARKER_BP, MARGIN_MARKER_TP, MARGIN_MARKER_EXEC, MARGIN_MARKER_EXEC_SIGNAL, MARGIN_MARKER_STACK = range(6)

	def __init__(self, distributed_objects, filename):
		QObject.__init__(self)
		filename = str(filename)
		self.distributed_objects = distributed_objects
		self.debug_controller = self.distributed_objects.debug_controller
		self.breakpoint_controller = self.distributed_objects.breakpoint_controller
		self.tracepoint_controller = self.distributed_objects.tracepoint_controller
		self.signalProxy = self.distributed_objects.signal_proxy
		self.filename = filename
		self.lastContexMenuLine = 0
		self.markerBp = QPixmap(":/markers/bp.png")
		self.markerTp = QPixmap(":/markers/tp.png")
		self.markerExec = QPixmap(":/markers/exec_pos.png")
		self.markerExecSignal = QPixmap(":/markers/exec_pos_signal.png")
		self.shown = False
		self.expToWatch = False

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
		self.edit.setTabWidth(4)
		self.edit.setLexer(self.lexer)
		self.edit.setWhitespaceVisibility(Qsci.QsciScintilla.WsVisible)
		self.edit.setIndentationGuides(True)
		self.edit.setMarginLineNumbers(self.MARGIN_NUMBERS, True)
		# set sensitivity
		self.edit.setMarginSensitivity(self.MARGIN_NUMBERS, True)
		self.edit.setMarginSensitivity(self.MARGIN_MARKER_BP, True)
		self.edit.setMarginSensitivity(self.MARGIN_MARKER_TP, True)
		# define symbol
		self.edit.markerDefine(self.markerBp, self.MARGIN_MARKER_BP)
		self.edit.markerDefine(self.markerTp, self.MARGIN_MARKER_TP)
		self.edit.markerDefine(self.markerExec, self.MARGIN_MARKER_EXEC)
		self.edit.markerDefine(self.markerExecSignal, self.MARGIN_MARKER_EXEC_SIGNAL)
		self.edit.markerDefine(Qsci.QsciScintilla.Background, self.MARGIN_MARKER_STACK)
		# define width and mask to show margin
		self.edit.setMarginWidth(self.MARGIN_MARKER_BP, 10)
		self.edit.setMarginMarkerMask(self.MARGIN_MARKER_BP, 1<<self.MARGIN_MARKER_BP)
		self.edit.setMarginWidth(self.MARGIN_MARKER_TP, 10)
		self.edit.setMarginMarkerMask(self.MARGIN_MARKER_TP, 1<<self.MARGIN_MARKER_TP)
		self.edit.setMarginWidth(self.MARGIN_MARKER_EXEC, 10)
		self.edit.setMarginMarkerMask(self.MARGIN_MARKER_EXEC, 1<<self.MARGIN_MARKER_EXEC | 1<<self.MARGIN_MARKER_EXEC_SIGNAL)
		self.edit.setMarginWidth(self.MARGIN_MARKER_STACK, 0)
		self.edit.setMarkerBackgroundColor(QColor(Qt.yellow), self.MARGIN_MARKER_STACK)
		self.edit.setMarginMarkerMask(self.MARGIN_MARKER_STACK, 1<<self.MARGIN_MARKER_STACK)
		# ...
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
		QObject.connect(self.edit, SIGNAL("modificationChanged(bool)"), self.__setFileModified)
		
		
		self.setMarginWidthByLineNumbers()
		self.edit.SendScintilla(Qsci.QsciScintilla.SCI_SETMOUSEDWELLTIME, 500)

		# override scintillas context menu with our own
		self.edit.SendScintilla(Qsci.QsciScintilla.SCI_USEPOPUP, 0)
		self.edit.setContextMenuPolicy(Qt.CustomContextMenu)
		QObject.connect(self.edit, SIGNAL('customContextMenuRequested(QPoint)'), self.showContextMenu)
		
		QObject.connect(self.edit, SIGNAL("marginClicked(int,int,Qt::KeyboardModifiers)"), self.marginClicked)
		QObject.connect(self.edit, SIGNAL("SCN_DOUBLECLICK(int, int, int)"), self.editDoubleClicked)
		QObject.connect(self.edit, SIGNAL("SCN_DWELLSTART(int, int, int)"), self.dwellStart)
		QObject.connect(self.edit, SIGNAL("SCN_DWELLEND(int, int, int)"), self.dwellEnd)
		
		# initially, read all breakpoints and tracepoints from the model
		self.getBreakpointsFromModel()
		self.getTracepointsFromModel()
		
		self.connect(self.breakpoint_controller.breakpointModel, SIGNAL('rowsInserted(QModelIndex, int, int)'), self.getBreakpointsFromModel)
		self.connect(self.breakpoint_controller.breakpointModel, SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.getBreakpointsFromModel)
		
		self.connect(self.distributed_objects.actions.actions[Actions.AddWatch], SIGNAL('triggered()'), self.addWatch)
		self.connect(self.distributed_objects.actions.actions[Actions.ToggleTrace], SIGNAL('triggered()'), self.toggleTracepoint)
		self.connect(self.distributed_objects.actions.actions[Actions.AddVarToDataGraph], SIGNAL('triggered()'), self.AddVarToDataGraph)
	
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
			
			logging.warning("Source file %s modified. Recompile executable for correct debugging.", self.filename)

		
	def __setFileModified(self, modified):
		''' Method called whenever current file is marked as modified '''
		self.distributed_objects.signal_proxy.emitFileModified(self.filename, modified)
			
	def dwellStart(self, pos, x, y):
		if self.edit.frameGeometry().contains(x, y):
			name = self.getWordOrSelectionFromPosition(pos)
			val = self.debug_controller.evaluateExpression(name.strip())
			if val != None:
				name = cgi.escape(name)
				val = cgi.escape(val)
				QToolTip.showText(self.edit.mapToGlobal(QtCore.QPoint(x, y)), "<b>"+name+"</b> = "+val, self.edit, QtCore.QRect())

	def dwellEnd(self, position, x, y):
		QToolTip.showText(self.edit.mapToGlobal(QtCore.QPoint(x, y)), "", self.edit, QtCore.QRect())
	
	def showContextMenu(self, point):
		scipos = self.edit.SendScintilla(Qsci.QsciScintilla.SCI_POSITIONFROMPOINT, point.x(), point.y())
		point = self.edit.mapToGlobal(point)
		exp = self.getWordOrSelectionFromPosition(scipos)
		# self.edit.lineIndexFromPosition(..) returns tupel. first of tupel is line
		self.lastContexMenuLine = int(self.edit.lineIndexFromPosition(scipos)[0])

		self.expToWatch = exp
		
		listOfTracepoints = self.tracepoint_controller.tracepointModel.getTracepoints()
		
		self.subPopupMenu = QtGui.QMenu(self.edit)
		self.subPopupMenu.setTitle("Add variable " + exp + " to...")
		
		for tp in listOfTracepoints:
			# dynamic actions, not in actiony.py Action class
			self.action = ActionEx(self.expToWatch, self)
			QObject.connect(self.action, SIGNAL("triggered(PyQt_PyObject)"), tp.addVar)
			self.action.setText(str(tp.name))
			self.action.setIcon(QIcon(QPixmap(":/icons/images/insert.png")))
			self.action.setIconVisibleInMenu(True)
			self.subPopupMenu.addAction(self.action)

		self.popupMenu = QtGui.QMenu(self.edit)
		# add watch and toggle breakpoint to menu
		self.popupMenu.addAction(self.distributed_objects.actions.actions[Actions.AddWatch])
		self.popupMenu.addAction(self.distributed_objects.actions.actions[Actions.ToggleTrace])
		self.popupMenu.addAction(self.distributed_objects.actions.actions[Actions.AddVarToDataGraph])
		# add separator and self.subPopupMenu
		self.popupMenu.addSeparator()
		self.popupMenu.addMenu(self.subPopupMenu)
		self.popupMenu.popup(point)
		
	def addWatch(self, watch=None):
		if watch:
			self.signalProxy.addWatch(watch)
		elif self.expToWatch:
			self.signalProxy.addWatch(self.expToWatch)
	
	def AddVarToDataGraph(self, watch=None):
		if watch:
			self.distributed_objects.datagraph_controller.addWatch(watch)
		elif self.expToWatch:
			self.distributed_objects.datagraph_controller.addWatch(self.expToWatch)

	def addWatchFloating(self, watch=None):
		if watch:
			self.signalProxy.addVarFloating(watch)
		elif self.expToWatch:
			self.signalProxy.addVarFloating(self.expToWatch)
	
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

	def getWordOrSelectionFromPosition(self, position):
		if self.isPositionInsideSelection(position):
			return str(self.edit.selectedText())
		else:
			return self.getWordFromPosition(position)
	
	def getWordFromPosition(self, position):
		line, col = self.edit.lineIndexFromPosition(position)
		s = str(self.edit.text(line))
		start = col
		end = col

		r = re.compile(r'[\w\d_]')
		while start>=0:
			if not r.match(s[start]):
				break
			start -= 1
		start += 1
		while end<len(s):
			if not r.match(s[end]):
				break
			end += 1
		return s[start:end]
	
	def editDoubleClicked(self, position, line, modifiers):
		w = self.getWordFromPosition(position)
		self.addWatch(str(w))
	
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
		self.edit.setMarginWidth(0, ceil(log(self.edit.lines(), 10))*10 + 5)
	
	def marginClicked(self, margin, line, state):
		# if breakpoint should be toggled
		if margin == self.MARGIN_NUMBERS or margin == self.MARGIN_MARKER_BP:
			self.toggleBreakpointWithLine(line)
		elif margin == self.MARGIN_MARKER_TP:
			self.toggleTracepointWithLine(line)
	
	def toggleBreakpointWithLine(self, line):
		self.breakpoint_controller.toggleBreakpoint(self.filename, line+1)-1
			
	def toggleTracepointWithLine(self, line):
		tpLine = self.tracepoint_controller.tracepointModel.toggleTracepoint(self.filename, line+1)-1
		if tpLine < 0:
			self.edit.markerDelete(line, self.MARGIN_MARKER_TP)
		else:
			self.edit.markerAdd(tpLine, self.MARGIN_MARKER_TP)
			
	def toggleTracepoint(self):
		self.toggleTracepointWithLine(self.lastContexMenuLine)
	
	def getBreakpointsFromModel(self, parent=None, start=None, end=None):
		"""Get breakpoints from model."""
		# TODO: don't reload all breakpoints, just the one referenced by parent/start/end
		self.edit.markerDeleteAll(self.MARGIN_MARKER_BP)
		for bp in self.breakpoint_controller.getBreakpointsFromModel():
			if bp.fullname == self.filename:
				self.edit.markerAdd(int(bp.line)-1, self.MARGIN_MARKER_BP)
		
	def getTracepointsFromModel(self):
		"""Get tracepoints from model."""
		self.edit.markerDeleteAll(self.MARGIN_MARKER_TP)
		for tp in self.tracepoint_controller.getTracepointsFromModel():
			if tp.fullname == self.filename:
				self.edit.markerAdd(int(tp.line)-1, self.MARGIN_MARKER_TP)
				

