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

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidget, QMessageBox
from .openedfileview import OpenedFileView
import os
import logging
import helpers.excep


class EditorView(QWidget):
    def __init__(self, distributedObjects, parent=None):
        QWidget.__init__(self, parent)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.distributedObjects = distributedObjects
        self.tabWidget.tabCloseRequested.connect(self.hideTab)
        self.tabWidget.currentChanged.connect(self.__changedTab)
        self.act = self.distributedObjects.actions

        self.openedFiles = {}

    def hideTab(self, idx):
        """ Close an opened file tab. Show message box if file has been modified. """
        w = self.tabWidget.widget(idx)

        ret = QMessageBox.Discard
        if self.__getFileModified(idx):
            msgBox = QMessageBox(QMessageBox.Question, "Save Resources", "'" +
                    self.tabWidget.tabText(idx)[:-1] +
                    "' has been modified. Save changes?", QMessageBox.Cancel |
                    QMessageBox.Save | QMessageBox.Discard, self)
            ret = msgBox.exec_()
            if ret == QMessageBox.Save:
                self.getCurrentOpenedFile().saveFile()

        if ret != QMessageBox.Cancel:
            for i in self.openedFiles.values():
                if w == i.tab:
                    if i.shown:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(i.tab))
                        i.shown = False
                    if i.filename in self.openedFiles:
                        del self.openedFiles[i.filename]
                    break
        return ret != QMessageBox.Cancel

    def __changedTab(self, idx):
        if self.__getFileModified(idx):
            self.act.SaveFile.setEnabled(True)
        else:
            self.act.SaveFile.setEnabled(False)

    def getCurrentOpenedFile(self):
        w = self.tabWidget.currentWidget()
        for i in self.openedFiles.values():
            if w == i.tab:
                return i

    def removeAllTabs(self):
        """ Method goes through opened files and asks user to save changes.
            returns false if user canceled operation
        """
        i = self.tabWidget.count()
        success = True
        while i > 0 and success:
            success = self.hideTab(i - 1)
            i = i - 1
        return success

    def isOpen(self, filename):
        return filename in self.openedFiles

    def openFile(self, filename):
        if not self.isOpen(filename):
            self.openedFiles[filename] = OpenedFileView(self.distributedObjects, filename, self)
            self.showFile(filename)
        self.openedFiles[filename].getBreakpointsFromModel()
        self.tabWidget.setCurrentWidget(self.openedFiles[filename].tab)

    def showFile(self, filename):
        opened_file = self.openedFiles[filename]
        if not opened_file.shown:
            self.tabWidget.addTab(opened_file.tab, os.path.basename(filename))
            self.tabWidget.setCurrentWidget(opened_file.tab)
            opened_file.shown = True

    def setFileModified(self, filename, modified):
        """ Adds a '*' to name of modified file in the editors tab widget.  """
        if filename in self.openedFiles:
            if (modified):
                self.tabWidget.setTabText(self.tabWidget.indexOf(
                    self.openedFiles[filename].tab),
                    os.path.basename(filename) + '*')
                self.act.SaveFile.setEnabled(True)
            else:
                self.tabWidget.setTabText(self.tabWidget.indexOf(
                    self.openedFiles[filename].tab),
                    os.path.basename(filename))
                self.act.SaveFile.setEnabled(False)

    def __getFileModified(self, idx):
        """ Method returns true if filename in tabwidget ends with '*'. """
        return str(self.tabWidget.tabText(idx)).endswith('*')

    def _targetStopped(self, rec):
        self.__removeExecutionPositionMarkers()

        # find the current execution position in the result
        file_ = None
        line = None
        for res in rec.results:
            if res.dest == "frame":
                try:
                    file_ = res.src.fullname
                except AttributeError:
                    try:
                        logging.warning("No source for %s found.", res.src.file)
                        raise helpers.excep.SourceFileNotFound(res.src.file)
                    except AttributeError:
                        logging.warning("No source file found.")
                        raise helpers.excep.SourceFileNotFound(None)
                line = int(res.src.line) - 1
                break

        self.openFile(file_)

        return file_, line

    def __removeExecutionPositionMarkers(self):
        for f in self.openedFiles.itervalues():
            f.clearExecutionPositionMarkers()

    def targetStoppedNormally(self, rec):
        file_, line = self._targetStopped(rec)
        self.openedFiles[file_].showExecutionPosition(line)

    def targetStoppedWithSignal(self, rec):
        file_, line = self._targetStopped(rec)
        self.openedFiles[file_].showSignalPosition(line)

    def targetExited(self):
        self.__removeExecutionPositionMarkers()
