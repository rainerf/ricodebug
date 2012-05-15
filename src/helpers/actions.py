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

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QAction, QIcon

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
class ActionEx(QAction):
    def __init__(self, parameter, parent=None):
        QAction.__init__(self, parent)
        self.parameter = parameter
        self.triggered.connect(self.commit)
        self.parent = parent

    # FIXME: this doesn't makes any sense
    def commit(self):
        print "---------------------------- commit ActionEx success."
        if self.parameter == None:
            print "------------------------ ActionEx: set paramter first!"
        else:
            print "------------------------ parameter ok."
            self.triggered(self.parameter)

class Actions(QObject):
    Open = Exit = SaveFile = Run = Continue = ReverseContinue = Interrupt = Next = \
        ReverseNext = Step = ReverseStep = Finish = RunToCursor = ToggleBreak = \
        ToggleTrace = AddTraceVar = DelTraveVar = AddWatch = AddVarToDataGraph = \
        DelWatch = Record = None

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        ###############################################
        ## file/program control
        ###############################################
        Actions.Open = self.createAction(":/icons/images/open.png", "Open", "Ctrl+O", \
                "Open executable file", self.Open)
        Actions.Exit = self.createAction(":/icons/images/exit.png", "Exit", "Ctrl+Q", \
                "Close Program", self.Exit)
        Actions.SaveFile = self.createAction(":/icons/images/save.png", "Save File", "Ctrl+S", \
                "Save source file", self.SaveFile)

        ###############################################
        ## file control
        ###############################################
        Actions.Run = self.createAction(":/icons/images/run.png", "Run", "F5", \
                "Run current executable")
        Actions.Continue = self.createAction(":/icons/images/continue.png", "Continue", "F6", \
                "Continue current executable")
        Actions.Interrupt = self.createAction(":/icons/images/interrupt.png", "Interrupt", "F4", \
                "Interrupt current executable")
        Actions.Next = self.createAction(":/icons/images/next.png", "Next", "F10", \
                "Execute next line")
        Actions.Step = self.createAction(":/icons/images/step.png", "Step", "F11", \
                "Next Step")
        Actions.Record = self.createAction(":/icons/images/record.png", \
                "Record", None, "Record gdb executions")
        Actions.ReverseNext = self.createAction(":/icons/images/rnext.png", "Reverse Next", None, \
                "Execute previous line")
        Actions.ReverseStep = self.createAction(":/icons/images/rstep.png", "Reverse Step", None, \
                "Previous Step")
        Actions.Finish = self.createAction(":/icons/images/finish.png", "Finish", None, \
                "Finish executable")
        Actions.RunToCursor = self.createAction(":/icons/images/until.png", "Run to Cursor", None, \
                "Run executable to cursor position")

        ###############################################
        ## watch/break/trace points
        ###############################################
        Actions.ToggleBreak = self.createAction(":/icons/images/bp.png", "Toggle Breakpoint", \
                "Ctrl+b", "Toggle breakpoint in current line")
        Actions.ToggleTrace = self.createAction(":/icons/images/tp.png", "Toggle Tracepoint", \
                "Ctrl+t", "Toggle tracepoint in current line")
        Actions.AddTraceVar = self.createAction(":/icons/images/tp_var_plus.png", \
                "Add var to Tracepoint", "+", \
                "Add selected variable to tracepoint")
        Actions.DelTraceVar = self.createAction(":/icons/images/tp_var_minus.png", \
                "Del var from Tracepoint", "-", \
                "Remove selected variable from tracepoint")
        Actions.AddWatch = self.createAction(":/icons/images/watch_plus.png", "Add var to Watch",\
                "+", "Add selected variable to watchview-window")
        Actions.AddVarToDataGraph = self.createAction(":/icons/images/watch_plus.png", \
                "Add var to DataGraph", "+", \
                "Add selected variable to datagraph-window",)
        Actions.DelWatch = self.createAction(":/icons/images/watch_minus.png", \
                "Del var from Watch", "+", \
                "Remove selected variable from watchview-window")

    def createAction(self, icon, text, shortcut, statustip, parameter=None):
        """dont use this function outside of class!!!"""
        if parameter is None:
            newAction = QAction(QIcon(icon), text, self.parent)
        else:
            newAction = None

        if shortcut is not None:
            newAction.setShortcut(shortcut)

        newAction.setStatusTip(statustip)
        return newAction


