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

from PyQt4.QtCore import QObject, pyqtSignal
from models.stackmodel import StackModel
from views.stackview import StackView
from helpers.icons import Icons


class StackController(QObject):
    stackFrameSelected = pyqtSignal()

    def __init__(self, distributedObjects):
        QObject.__init__(self)
        self.distributedObjects = distributedObjects
        self.__showMarkers = False

        self.editorController = distributedObjects.editorController

        self.stackModel = StackModel(self, self.distributedObjects.debugController, self.distributedObjects.gdb_connector)

        self.stackView = self.distributedObjects.buildView(StackView, "Stack", Icons.stack)
        self.stackView.setModel(self.stackModel)
        self.stackView.activated.connect(self.stackInStackViewActivated)

        self.distributedObjects.signalProxy.inferiorStoppedNormally.connect(self.stackModel.update)
        self.distributedObjects.signalProxy.inferiorHasExited.connect(self.stackModel.clear)
        self.distributedObjects.signalProxy.executableOpened.connect(self.stackModel.clear)
        self.distributedObjects.signalProxy.inferiorIsRunning.connect(self.removeStackMarkers)
        self.stackView.showStackTraceChanged.connect(self.showStackTraceChanged)

        self.stackModel.layoutChanged.connect(self.__updateStackMarkers)

    def stackInStackViewActivated(self, index):
        item = index.internalPointer()
        self.distributedObjects.gdb_connector.selectStackFrame(item.level)
        self.distributedObjects.signalProxy.openFile(item.fullname, item.line)
        self.stackFrameSelected.emit()

    def insertStackMarkers(self):
        for entry in self.stackModel.stack:
            if int(entry.level) != 0 and hasattr(entry, "fullname") and hasattr(entry, "line"):
                self.editorController.addStackMarker(entry.fullname, entry.line)

    def removeStackMarkers(self):
        for entry in self.stackModel.stack:
            if int(entry.level) != 0 and hasattr(entry, "fullname"):
                self.editorController.delStackMarkers(entry.fullname)

    def showStackTraceChanged(self, state):
        self.__showMarkers = state
        if self.__showMarkers:
            self.insertStackMarkers()
        else:
            self.removeStackMarkers()

    def __updateStackMarkers(self):
        if self.__showMarkers:
            self.insertStackMarkers()
