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

from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from models.stackmodel import StackModel
from views.stackview import StackView

class StackController(QObject):
    def __init__(self, distributed_objects):
        QObject.__init__(self)
        self.distributed_objects = distributed_objects
        
        self.editorController = distributed_objects.editor_controller
        
        self.stackModel = StackModel(self, self.distributed_objects.debug_controller, self.distributed_objects.gdb_connector)
        self.stackView = StackView(self)
        
        self.stackView.stackView.setModel(self.stackModel)
        
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorStoppedNormally(PyQt_PyObject)'), self.stackModel.update)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorHasExited(PyQt_PyObject)'), self.stackModel.clear)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('executableOpened()'), self.stackModel.clear)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorIsRunning(PyQt_PyObject)'), self.removeStackMarkers)
        QObject.connect(self.stackView.showStackTrace, SIGNAL('stateChanged(int)'), self.showStackTraceChanged)
        
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        
    def insertDockWidgets(self):
        self.stackDock = QDockWidget("Stack")
        self.stackDock.setObjectName("StackView")
        self.stackDock.setWidget(self.stackView)
        self.distributed_objects.signal_proxy.addDockWidget(Qt.BottomDockWidgetArea, self.stackDock, True)
        
    def stackInStackViewActivated(self, index):
        item = index.internalPointer()
        self.distributed_objects.gdb_connector.selectStackFrame(item.level)
        self.distributed_objects.signal_proxy.openFile(item.fullname, item.line)
        # FIXME: make locals view etc change their view too!
        
    def insertStackMarkers(self):
        if self.stackView.showStackTrace.checkState() == Qt.Checked:
            for entry in self.stackModel.stack:
                if int(entry.level) != 0 and hasattr(entry, "fullname") and hasattr(entry, "line"):
                    self.editorController.addStackMarker(entry.fullname, entry.line)
    
    def removeStackMarkers(self):
        for entry in self.stackModel.stack:
            if int(entry.level) != 0 and hasattr(entry, "fullname"):
                self.editorController.delStackMarkers(entry.fullname)
                
    def showStackTraceChanged(self, state):
        if state == Qt.Checked:
            self.insertStackMarkers()
        elif state == Qt.Unchecked:
            self.removeStackMarkers()
    
