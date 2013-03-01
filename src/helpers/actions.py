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
from PyQt4.QtGui import QStyle, QApplication, QIcon, QAction
from helpers.icons import Icons

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


class Actions(QObject):
    class ActionEx(QAction):
        triggeredEx = pyqtSignal('PyQt_PyObject')

        def __init__(self, parameter, parent=None):
            QAction.__init__(self, parent)
            self.parameter = parameter
            self.triggered.connect(self.commit)

        def commit(self):
            assert(self.parameter is not None)
            self.triggeredEx.emit(self.parameter)

    def __init__(self):
        QObject.__init__(self)

        def _icon(type_):
            return

        ###############################################
        # # file/program control
        ###############################################
        # open
        self.Open = self.__createAction(QStyle.SP_DialogOpenButton, "Open",
                "Ctrl+O", "Open executable file")

        self.OpenMenu = self.__createAction(QStyle.SP_DialogOpenButton, "Open",
                "Ctrl+O", "Open executable file")
        # exit
        self.Exit = self.__createAction(QStyle.SP_DialogCloseButton, "Exit",
                "Ctrl+Q", "Close Program")
        # save source file
        self.SaveFile = self.__createAction(QStyle.SP_DialogSaveButton,
                "Save File", "Ctrl+S", "Save source file")

        ###############################################
        # # file control
        ###############################################
        # run
        self.Run = self.__createAction(":/icons/images/run.png", "Run", "F5",
                "Run current executable")
        # continue
        self.Continue = self.__createAction(":/icons/images/continue.png",
                "Continue", "F6", "Continue current executable")
        # interrupt
        self.Interrupt = self.__createAction(":/icons/images/interrupt.png",
                "Interrupt", "F4", "Interrupt current executable")
        # next
        self.Next = self.__createAction(":/icons/images/next.png", "Next", "F10",
                "Execute next line")
        # step
        self.Step = self.__createAction(":/icons/images/step.png", "Step", "F11",
                "Next Step")
        # record
        self.Record = self.__createAction(":/icons/images/record.png", "Record",
                None, "Record gdb executions")
        # previous
        self.ReverseNext = self.__createAction(":/icons/images/rnext.png",
                "Reverse Next", None, "Execute previous line")
        # reverse step
        self.ReverseStep = self.__createAction(":/icons/images/rstep.png",
                "Reverse Step", None, "Previous Step")
        # finish
        self.Finish = self.__createAction(":/icons/images/finish.png", "Finish",
                None, "Finish executable")
        # run to cursor
        self.RunToCursor = self.__createAction(":/icons/images/until.png",
                "Run to Cursor", None, "Run executable to cursor position")

        ###############################################
        # # watch/break/trace points
        ###############################################
        # toggle breakpoint
        self.ToggleBreak = self.__createAction(":/icons/images/bp.png",
                "Toggle Breakpoint", "Ctrl+b",
                "Toggle breakpoint in current line")
        # add tracepoint
        self.ToggleTrace = self.__createAction(":/icons/images/tp.png",
                "Toggle Tracepoint", "Ctrl+t",
                "Toggle tracepoint in current line")
        # AddTraceVar
        self.AddTraceVar = self.__createAction(":/icons/images/tp_var_plus.png",
                "Add var to Tracepoint", "+",
                "Add selected variable to tracepoint")
        # DelTraceVar
        self.DelTraveVar = self.__createAction(":/icons/images/tp_var_minus.png",
                "Del var from Tracepoint", "-",
                "Remove selected variable from tracepoint")
        # DelWatch
        self.DelWatch = self.__createAction(":/icons/images/watch_minus.png",
                "Del var from Watch", "+",
                "Remove selected variable from watchview-window")

    def getAddToWatchAction(self, name, slot):
        a = self.createEx(name)
        a.setText("Add '%s' to watch window" % name)
        a.setToolTip("Add selected variable to watchview window")
        a.setIcon(Icons.watch)
        a.triggeredEx.connect(slot)
        return a

    def getAddToDatagraphAction(self, name, slot):
        a = self.createEx(name)
        a.setText("Add '%s' to datagraph window" % name)
        a.setToolTip("Add selected variable to datagraph window")
        a.setIcon(Icons.datagraph)
        a.triggeredEx.connect(slot)
        return a

    def getAddToTracepointAction(self, varname, tpname, slot):
        a = self.createEx(varname)
        a.setText(str(tpname))
        a.setIcon(Icons.tp)
        a.setIconVisibleInMenu(True)
        a.triggeredEx.connect(slot)
        return a

    def getAddWatchpointAction(self, name, slot):
        a = self.createEx(name)
        a.setText("Set watchpoint on '%s'" % name)
        a.setIcon(Icons.wp)
        a.triggeredEx.connect(slot)
        return a

    def createEx(self, parameter):
        return self.ActionEx(parameter, self)

    def __createAction(self, icon, text, shortcut, statustip):
        if isinstance(icon, basestring):
            icon = QIcon(icon)
        else:
            icon = QApplication.style().standardIcon(icon)

        newAction = QAction(icon, text, self)

        if shortcut is not None:
            newAction.setShortcut(shortcut)

        return newAction
