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

"""@package breakpointcontroller
    the breakpoint controller
"""

from PyQt4.QtCore import QObject, Qt
from models.breakpointmodel import BreakpointModel
from views.breakpointview import BreakpointView


class BreakpointController(QObject):
    def __init__(self, distributedObjects):
        """ init breakpoint controller and members.
        @param distributedObjects: passing distributed objects
        @note There are following signals: \n
            * insertDockWidgets() : necessary for plugin system\n
            * cleanupModels(): clear Breakpoints\n
        """
        QObject.__init__(self)
        self.distributedObjects = distributedObjects

        self._model = BreakpointModel(self.distributedObjects.gdb_connector)
        self.breakpointView = BreakpointView()

        self.breakpointView.breakpointView.setModel(self._model)

        #register with session manager to save breakpoints
        self.distributedObjects.signalProxy.emitRegisterWithSessionManager(self, "Breakpoints")

        self.distributedObjects.signalProxy.cleanupModels.connect(self._model.clearBreakpoints)

        self.distributedObjects.mainwindow.insertDockWidget(self.breakpointView, "Breakpoints", Qt.BottomDockWidgetArea, True)

    def insertBreakpoint(self, file_, line):
        """insert a breakpoint in specified file on specified line
        @param file: (string), full name (incl. path) of file where breakpoint should be inserted
        @param line: (integer), line number where breakpoint should be inserted
        @return: (integer), returns the line as number where the breakpoint finally is inserted
        @note sometimes it is not possible for gdb to insert a breakpoint on specified line because the line is
        empty or has no effect. therefore it is necessary to observe the real line number of inserted breakpoint
        """
        return self._model.insertBreakpoint(file_, line)

    def deleteBreakpoint(self, file_, line):
        """deletes a breakpoint in specified file on specified line
        @param file: (string), full name (incl. path) of file
        @param line: (int), line number where breakpoint should be deleted
        """
        self._model.deleteBreakpoint(file_, line)

    def toggleBreakpoint(self, file_, line):
        """ toggles the breakpoint in file file_ with linenumber line
        @param file_: (string), fullname of file
        @param line: (int), linenumber where the breakpoint should be toggled
        """
        return self._model.toggleBreakpoint(file_, line)

    def getBreakpointsFromModel(self):
        """returns a list of all breakpoints in model
        @return breakpoints: (List<ExtendedBreakpoint>), a list of breakpoints
        """
        return self._model.getBreakpoints()

    def setBreakpointsForModel(self, bpList):
        self._model.setBreakpoints(bpList)

    def saveSession(self, xmlHandler):
        """Insert session info to xml file"""
        bpparent = xmlHandler.createNode("Breakpoints")
        for bp in self._model.getBreakpoints():
            xmlHandler.createNode("Breakpoint", bpparent, {"file": bp.file, "line": bp.line})

    def loadSession(self, xmlHandler):
        """load session info to xml file"""
        bpparent = xmlHandler.getNode("Breakpoints")
        if bpparent != None:
            childnodes = bpparent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self._model.insertBreakpoint(attr["file"], attr["line"])

    def model(self):
        return self._model
