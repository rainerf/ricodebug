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

from PyQt4.QtCore import QObject, SIGNAL
from editorview import EditorView

class EditorController(QObject):        
    def __init__(self, distributed_objects):
        QObject.__init__(self)
        self.distributed_objects = distributed_objects
        
        self.editor_view = EditorView(self.distributed_objects);
        
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorStoppedNormally(PyQt_PyObject)'), self.editor_view.targetStoppedNormally)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorReceivedSignal(PyQt_PyObject)'), self.editor_view.targetStoppedWithSignal)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('inferiorHasExited(PyQt_PyObject)'), self.editor_view.targetExited)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('saveFile()'), self.saveCurrentFile)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL('fileModified(PyQt_PyObject, bool)'), self.editor_view.setFileModified) 
        
    def jumpToLine(self, filename, line):
        line = int(line) - 1
        self.editor_view.openFile(filename)
        file_ = self.editor_view.openedFiles[filename]
        file_.showLine(line)
        editor = file_.edit
        editor.setSelection(line, 0, line, editor.lineLength(line))
        
    def addStackMarker(self, filename, line):
        line = int(line) - 1
        self.editor_view.openFile(filename)
        file_ = self.editor_view.openedFiles[filename]
        editor = file_.edit
        editor.markerAdd(line, file_.MARGIN_MARKER_STACK)
    
    def delStackMarkers(self, filename):
        self.editor_view.openFile(filename)
        file_ = self.editor_view.openedFiles[filename]
        editor = file_.edit
        editor.markerDeleteAll(file_.MARGIN_MARKER_STACK)
            
    def saveCurrentFile(self):
        self.editor_view.getCurrentOpenedFile().saveFile()
        
    def closeOpenedFiles(self):
        return self.editor_view.removeAllTabs()
