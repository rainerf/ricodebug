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

from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from breakpointmodel import BreakpointModel
from breakpointview import BreakpointView



class BreakpointController(QObject):
    """ Class contains tracepointModel and tracepointView """
    
    def __init__(self, distributed_objects):
        """ init tracepoint controller and members.
        @param distributed_objects: passing distributed objects
        @note There are following signals: \n
            * insertDockWidgets() : necessary for plugin system\n
            * cleanupModels(): clear Tracepoints\n
        """
        QObject.__init__(self)
        self.distributed_objects = distributed_objects
        
        self.breakpointModel = BreakpointModel(self.distributed_objects.gdb_connector)
        self.breakpointView = BreakpointView()
        
        self.breakpointView.breakpointView.setModel(self.breakpointModel)
        
        #register with session manager to save breakpoints
        self.distributed_objects.signal_proxy.emitRegisterWithSessionManager(self, "Breakpoints")
        
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL("insertDockWidgets()"), self.insertDockWidgets)
        QObject.connect(self.distributed_objects.signal_proxy, SIGNAL("cleanupModels()"), self.breakpointModel.clearBreakpoints)
        
    def insertDockWidgets(self):
        """ needed for plugin system"""
        self.breakpointDock = QDockWidget("Breakpoints")
        self.breakpointDock.setObjectName("BreakpointView")
        self.breakpointDock.setWidget(self.breakpointView)
        self.distributed_objects.signal_proxy.addDockWidget(Qt.BottomDockWidgetArea, self.breakpointDock, True)
        
    def insertBreakpoint(self, file_, line):
        """insert a breakpoint in specified file on specified line
        @param file: (string), full name (incl. path) of file where breakpoint should be inserted
        @param line: (integer), line number where breakpoint should be inserted
        @return: (integer), returns the line as number where the breakpoint finally is inserted
        @note sometimes it is not possible for gdb to insert a breakpoint on specified line because the line is
        empty or has no effect. therefore it is necessary to observe the real line number of inserted breakpoint
        """
        return self.breakpointModel.insertBreakpoint(file_, line)
    
    def deleteBreakpoint(self, file_, line):
        """deletes a breakpoint in specified file on specified line
        @param file: (string), full name (incl. path) of file
        @param line: (int), line number where breakpoint should be deleted
        """
        self.breakpointModel.deleteBreakpoint(file_, line)
        
    def getBreakpointsFromModel(self):
        """returns a list of all breakpoints in model
        @return breakpoints: (List<ExtendedBreakpoint>), a list of breakpoints
        """
        return self.breakpointModel.getBreakpoints()
        
    def setBreakpointsForModel(self, bpList):
        self.breakpointModel.setBreakpoints(bpList)
            
    def saveSession(self, xmlHandler):
        """Insert session info to xml file"""
        bpparent = xmlHandler.createNode("Breakpoints")
        for bp in self.breakpointModel.getBreakpoints():
            xmlHandler.createNode("Breakpoint", bpparent, { "file": bp.file, "line": bp.line })
             
    def loadSession(self, xmlHandler): 
        """load session info to xml file"""      
        bpparent = xmlHandler.getNode("Breakpoints")
        if bpparent != None:
            childnodes = bpparent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self.breakpointModel.insertBreakpoint(attr["file"], attr["line"])
            

            
            
            
            
            
            
