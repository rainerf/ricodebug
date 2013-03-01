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
from PyQt4.QtGui import QStyle, QApplication, QIcon, QAction, QPixmap, QImage
from helpers.icons import Icons


class ActionEx(QAction):
    triggeredEx = pyqtSignal('PyQt_PyObject')

    def __init__(self, parameter, parent=None):
        QAction.__init__(self, parent)
        self.parameter = parameter
        self.triggered.connect(self.commit)

    def commit(self):
        assert(self.parameter is not None)
        self.triggeredEx.emit(self.parameter)


class Actions(QObject):
    def __init__(self, do):
        QObject.__init__(self)

        def _mirrored(icon):
            return QPixmap.fromImage(QImage(QPixmap(icon)).mirrored(True, False))

        ###############################################
        # # file/program control
        ###############################################
        self.Open = self.__createAction(QStyle.SP_DialogOpenButton, "Open",
                None, "Open executable file")
        self.Open.triggered.connect(do.mainwindow.showOpenExecutableDialog)

        self.OpenMenu = self.__createAction(QStyle.SP_DialogOpenButton, "Open",
                "Ctrl+O", "Open executable file")
        self.OpenMenu.triggered.connect(do.mainwindow.showOpenExecutableDialog)

        self.Exit = self.__createAction(QStyle.SP_DialogCloseButton, "Exit",
                "Ctrl+Q", "Close Program")
        self.Exit.triggered.connect(do.mainwindow.close)

        self.SaveFile = self.__createAction(QStyle.SP_DialogSaveButton,
                "Save File", "Ctrl+S", "Save source file")
        self.SaveFile.triggered.connect(do.signalProxy.saveFile.emit)

        ###############################################
        # # file control
        ###############################################
        self.Run = self.__createAction(":/icons/images/run.png", "Run", "F5",
                "Run current executable")
        self.Run.triggered.connect(do.debugController.run)

        self.Continue = self.__createAction(":/icons/images/continue.png",
                "Continue", "F6", "Continue current executable")
        self.Continue.triggered.connect(do.debugController.cont)

        self.Interrupt = self.__createAction(":/icons/images/interrupt.png",
                "Interrupt", "F4", "Interrupt current executable")
        self.Interrupt.triggered.connect(do.debugController.interrupt)

        self.Next = self.__createAction(":/icons/images/next.png", "Next", "F10",
                "Execute next line")
        self.Next.triggered.connect(do.debugController.next_)

        self.Step = self.__createAction(":/icons/images/step.png", "Step", "F11",
                "Next Step")
        self.Step.triggered.connect(do.debugController.step)

        self.Finish = self.__createAction(":/icons/images/finish.png", "Finish",
                None, "Finish executable")
        self.Finish.triggered.connect(do.debugController.finish)

        self.RunToCursor = self.__createAction(":/icons/images/until.png",
                "Run to Cursor", None, "Run executable to cursor position")
        self.RunToCursor.triggered.connect(do.debugController.inferiorUntil)

        self.Record = self.__createAction(":/icons/images/record.png", "Record",
                None, "Record gdb executions")
        self.Record.triggered.connect(do.debugController.setRecord)

        self.ReverseNext = self.__createAction(_mirrored(":/icons/images/next.png"),
                "Reverse Next", None, "Execute previous line")
        self.ReverseNext.triggered.connect(do.debugController.reverse_next)

        self.ReverseStep = self.__createAction(_mirrored(":/icons/images/step.png"),
                "Reverse Step", None, "Previous Step")
        self.ReverseStep.triggered.connect(do.debugController.reverse_step)

        self.ReverseFinish = self.__createAction(_mirrored(":/icons/images/finish.png"),
                "Reverse Step", None, "Previous Step")  # finish
        self.ReverseFinish.triggered.connect(do.debugController.reverse_finish)

        ###############################################
        # # watch/break/trace points
        ###############################################
        self.ToggleBreak = self.__createAction(":/icons/images/bp.png",
                "Toggle Breakpoint", "Ctrl+b",
                "Toggle breakpoint in current line")
        self.ToggleTrace = self.__createAction(":/icons/images/tp.png",
                "Toggle Tracepoint", "Ctrl+t",
                "Toggle tracepoint in current line")
        self.AddTraceVar = self.__createAction(":/icons/images/tp_var_plus.png",
                "Add var to Tracepoint", "+",
                "Add selected variable to tracepoint")
        self.DelTraveVar = self.__createAction(":/icons/images/tp_var_minus.png",
                "Del var from Tracepoint", "-",
                "Remove selected variable from tracepoint")
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
        return ActionEx(parameter, self)

    def __createAction(self, icon, text, shortcut, statustip):
        if isinstance(icon, QStyle.StandardPixmap):
            icon = QApplication.style().standardIcon(icon)
        else:
            icon = QIcon(icon)

        newAction = QAction(icon, text, self)

        if shortcut is not None:
            newAction.setShortcut(shortcut)

        return newAction
