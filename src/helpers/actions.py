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

"""
general information:
 * to add a action write a enum-Key-word into list below class declaration 
   and raise range in both, range after list AND range for 
   self.actions = rang(N) dont forget "\" if line is ending
 * then create the action using createAction function in initActions 
   from Actions class:
    ...
    def initActions(self):
        # your action name
        self.createActions(<params for your action as string>)
    ...
 * connect your actions via connectAction or connectActionEx or your own Implementation
"""

class Actions(QtCore.QObject):
    class ActionEx(QtGui.QAction):
        def __init__(self, parameter, parent=None):
            QtGui.QAction.__init__(self, parent)
            self.parameter = parameter
            self.tiggered.connect(self.commit)
            self.parent = parent

        def commit(self):
            assert(self.parameter is not None)
            self.triggered.emit(self.parameter)

    def __init__(self):
        QtCore.QObject.__init__(self)
        ###############################################
        ## file/program control
        ###############################################
        #open
        self.Open = self.__createAction(":/icons/images/open.png", "Open", 
                "Ctrl+O", "Open executable file")
        #exit
        self.Exit = self.__createAction(":/icons/images/exit.png", "Exit", 
                "Ctrl+Q", "Close Program")
        #save source file
        self.SaveFile = self.__createAction(":/icons/images/save.png",
                "Save File", "Ctrl+S", "Save source file")

        ###############################################
        ## file control
        ###############################################
        #run
        self.Run = self.__createAction(":/icons/images/run.png", "Run", "F5",
                "Run current executable")
        #continue
        self.Continue = self.__createAction(":/icons/images/continue.png",
                "Continue", "F6", "Continue current executable")
        #interrupt
        self.Interrupt = self.__createAction(":/icons/images/interrupt.png",
                "Interrupt", "F4", "Interrupt current executable")
        #next
        self.Next = self.__createAction(":/icons/images/next.png", "Next", "F10",
                "Execute next line")
        #step
        self.Step = self.__createAction(":/icons/images/step.png", "Step", "F11",
                "Next Step")
        #record
        self.Record = self.__createAction(":/icons/images/record.png", "Record",
                None, "Record gdb executions")
        #previous
        self.ReverseNext = self.__createAction(":/icons/images/rnext.png",
                "Reverse Next", None, "Execute previous line")
        #reverse step
        self.ReverseStep = self.__createAction(":/icons/images/rstep.png",
                "Reverse Step", None, "Previous Step")
        #finish
        self.Finish = self.__createAction(":/icons/images/finish.png", "Finish",
                None, "Finish executable")
        #run to cursor
        self.RunToCursor = self.__createAction(":/icons/images/until.png",
                "Run to Cursor", None, "Run executable to cursor position")

        ###############################################
        ## watch/break/trace points
        ###############################################
        #toggle breakpoint
        self.ToggleBreak = self.__createAction(":/icons/images/bp.png",
                "Toggle Breakpoint", "Ctrl+b",
                "Toggle breakpoint in current line")
        #add tracepoint
        self.ToggleTrace = self.__createAction(":/icons/images/tp.png",
                "Toggle Tracepoint", "Ctrl+t",
                "Toggle tracepoint in current line")
        #AddTraceVar
        self.AddTraceVar = self.__createAction(":/icons/images/tp_var_plus.png",
                "Add var to Tracepoint", "+",
                "Add selected variable to tracepoint")
        #DelTraceVar
        self.DelTraveVar = self.__createAction(":/icons/images/tp_var_minus.png",
                "Del var from Tracepoint", "-",
                "Remove selected variable from tracepoint")
        #AddWatch
        self.AddWatch = self.__createAction(":/icons/images/watch_plus.png",
                "Add var to Watch", "+",
                "Add selected variable to watchview-window")
        #AddToDataGraph
        self.AddVarToDataGraph = self.__createAction(":/icons/images/watch_plus.png",
                "Add var to DataGraph", "+",
                "Add selected variable to datagraph-window")
        #DelWatch
        self.DelWatch = self.__createAction(":/icons/images/watch_minus.png",
                "Del var from Watch", "+",
                "Remove selected variable from watchview-window")

    def createEx(self, parameter):
        return self.ActionEx(parameter)

    def __createAction(self, icon, text, shortcut, statustip):
        """dont use this function outside of class!!!"""
        
        newAction = QtGui.QAction(QtGui.QIcon(icon), text, self)

        if shortcut is not None:
            newAction.setShortcut(shortcut)
        
        return newAction

