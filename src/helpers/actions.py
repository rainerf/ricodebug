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
from PyQt4.QtCore import SIGNAL, QObject

"""
general information:
 * to add a action write a enum-Key-word into list below class declaration and raise range 
   in both, range after list AND range for self.actions = rang(N)
   dont forget "\" if line is ending
 * then create the action using createAction function in initActions from Actions class:
    ...
    def initActions(self):
        # your action name
        self.createActions(<params for your action as string>)
    ...
 * connect your actions via connectAction or connectActionEx or your own Implementation
"""

class ActionEx(QtGui.QAction):
    
    def __init__(self, parameter, parent = None):
        QtGui.QAction.__init__(self, parent)
        self.parameter = parameter
        QObject.connect(self, SIGNAL("triggered()"), self.commit)
        self.parent = parent
        
    def commit(self):
        print "---------------------------- commit ActionEx success."
        if self.parameter == None:
            print "------------------------ ActionEx: set paramter first!"
        else:
            print "------------------------ parameter ok."
            self.emit(QtCore.SIGNAL("triggered(PyQt_PyObject)"), self.parameter)
        

class Actions(QtCore.QObject):
    NumActions = 17
    Open, Exit, SaveFile,\
    Run, Continue, Interrupt, Next, Step, Finish, RunToCursor,\
    ToggleBreak, ToggleTrace, AddTraceVar, DelTraveVar, \
    AddWatch, AddVarToDataGraph, DelWatch = range(NumActions)
    
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.actions = [None for i in range(self.NumActions)]
        self.initGlobalActions()
        
    def add(self, enum, action):
        """dont use this function outside of class!!!"""
        self.actions[enum] = action
        
    def createAction(self, icon, text, shortcut, statustip, enum, parameter = None):
        """dont use this function outside of class!!!"""
        if parameter == None:
            newAction = QtGui.QAction(QtGui.QIcon(icon), text, self)
        else:
            newAction = ActionEx(parameter)
        if shortcut != None:
            newAction.setShortcut(shortcut)
        newAction.setStatusTip(statustip)
        self.add(enum, newAction)
        
    def initGlobalActions(self):
        
        ###############################################
        ## file/program control
        ###############################################
        #open
        self.createAction(":/icons/images/open.png", "Open", "Ctrl+O", "Open executable file", self.Open)
        #exit
        self.createAction(":/icons/images/exit.png", "Exit", "Ctrl+Q", "Close Program", self.Exit)
        #save source file
        self.createAction(":/icons/images/save.png", "Save File", "Ctrl+S", "Save source file", self.SaveFile)
        
        ###############################################
        ## file control
        ###############################################
        #run
        self.createAction(":/icons/images/run.png", "Run", "F5", "Run current executable", self.Run)
        #continue
        self.createAction(":/icons/images/continue.png", "Continue", "F6", "Continue current executable", self.Continue)
        #interrupt
        self.createAction(":/icons/images/interrupt.png", "Interrupt", "F4", "Interrupt current executable", self.Interrupt)
        #next
        self.createAction(":/icons/images/next.png", "Next", "F10", "execute next line", self.Next)
        #step
        self.createAction(":/icons/images/step.png", "Step", "F11", "next Step", self.Step)
        #finish
        self.createAction(":/icons/images/finish.png", "Finish", None, "Finish executable", self.Finish)
        #run to cursor
        self.createAction(":/icons/images/until.png", "Run to Cursor", None, "Run executable to cursor position", self.RunToCursor)
        
        ###############################################
        ## watch/break/trace points
        ###############################################
        #toggle breakpoint
        self.createAction(":/icons/images/bp.png", "Toggle Breakpoint", "Ctrl+b", "Toggle breakpoint in current line", self.ToggleBreak)
        #add tracepoint
        self.createAction(":/icons/images/tp.png", "Toggle Tracepoint", "Ctrl+t", "Toggle tracepoint in current line", self.ToggleTrace)
        #AddTraceVar
        self.createAction(":/icons/images/tp_var_plus.png", "Add var to Tracepoint", "+", "Add selected variable to tracepoint", self.AddTraceVar)
        #DelTraceVar
        self.createAction(":/icons/images/tp_var_minus.png", "Del var from Tracepoint", "-", "Remove selected variable from tracepoint", self.DelTraveVar)
        #AddWatch
        self.createAction(":/icons/images/watch_plus.png", "Add var to Watch", "+", "Add selected variable to watchview-window", self.AddWatch)
        #AddToDataGraph
        self.createAction(":/icons/images/watch_plus.png", "Add var to DataGraph", "+", "Add selected variable to datagraph-window", self.AddVarToDataGraph)
        #DelWatch
        self.createAction(":/icons/images/watch_minus.png", "Del var from Watch", "+", "Remove selected variable from watchview-window", self.DelWatch)
 
        ###############################################
        ## <your description>
        ###############################################
        
        
        
        
        
        
        
        
        
        
