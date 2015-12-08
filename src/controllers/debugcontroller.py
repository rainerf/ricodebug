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

import os
import logging
from collections import defaultdict

from PyQt4.QtCore import QObject, pyqtSignal, Qt, QFileSystemWatcher, pyqtSlot
from PyQt4.QtGui import QAction

from helpers.ptyhandler import PtyHandler
from helpers.gdboutput import GdbOutput
from helpers.configstore import ConfigSet, ConfigItem
from helpers.excep import GdbError
from helpers.icons import Icons
from helpers.tracer import trace
import itertools


class DebugConfig(ConfigSet):
    def __init__(self):
        ConfigSet.__init__(self, "Debugging", "Debugging Options", Icons.namespace)
        self.breakAtMain = ConfigItem(self, "Break at main function", True)


class DebugController(QObject):
    executableOpened = pyqtSignal('PyQt_PyObject')

    def __init__(self, do):
        QObject.__init__(self)

        self.ptyhandler = PtyHandler()

        self.do = do

        self.connector = self.do.gdb_connector
        self.signalProxy = self.do.signalProxy

        self.executableName = None
        self.lastCmdWasStep = False

        self.ptyhandler.start()
        self.connector.start()

        self.connector.reader.asyncRecordReceived.connect(self.handleAsyncRecord, Qt.QueuedConnection)

        self.__config = DebugConfig()
        self.do.configStore.registerConfigSet(self.__config)
        self.__config.itemsHaveChanged.connect(self.updateConfig)

        self.__binaryWatcher = QFileSystemWatcher()
        self.__binaryWatcher.fileChanged.connect(self.__binaryChanged)

        self.do.signalProxy.addProxy(["openExecutable", "run", "setRecord", "next_", "reverse_next", "step", "reverse_step", "cont", "interrupt", "finish", "reverse_finish", "evaluateExpression", "executeCliCommand", "inferiorUntil", "getStackDepth", "selectStackFrame"], self)


    def __reloadAction(self):
        a = QAction("Reload", self)
        a.triggered.connect(lambda: self.openExecutable(self.executableName))
        return a

    def __binaryChanged(self):
        """ Slot for FileWatcher - Using QtMessagebox for interaction"""
        logging.warning("The executable was changed on the disc. Please reload the file.",
                        extra={"actions": [self.__reloadAction()]})

    def updateConfig(self):
        if self.executableName:
            logging.warning("Configuration changed. Please reload executable for changes to take effect!",
                            extra={"actions": [self.__reloadAction()]})

    @trace
    @pyqtSlot(str)
    def openExecutable(self, filename):
        # make sure we only open absolute paths, otherwise eg. RecentFileHandler
        # will not know _where_ the file was we opened and store different
        # relative paths for the same file
        filename = os.path.abspath(filename)

        if not os.path.exists(filename):
            logging.error("File %s was not found.", filename)
            return

        if self.do.editorController.closeOpenedFiles():  # closing source files may be canceled by user
            if self.executableName is not None:
                # clear variables, tracepoints, watches,... by connecting to this signal
                self.signalProxy.cleanupModels.emit()
                self.__binaryWatcher.removePath(self.executableName)

            self.connector.changeWorkingDirectory(os.path.dirname(filename))
            self.connector.openFile(filename)
            if self.__config.breakAtMain.value:
                self.do.breakpointModel.insertBreakpoint("main", None)
            self.executableOpened.emit(filename)
            self.executableName = filename
            self.__binaryWatcher.addPath(self.executableName)

    @trace
    @pyqtSlot(str)
    def run(self, args=None):
        self.connector.setTty(self.ptyhandler.ptyname)
        if not args:
            args = ""
        self.connector.setArgs(args)
        try:
            self.connector.run()
            self.lastCmdWasStep = False
            self.signalProxy.runClicked.emit()
        except GdbError:
            pass

    @trace
    @pyqtSlot(int)
    def setRecord(self, state):
        if state:
            self.connector.record_start()
        else:
            self.connector.record_stop()
        self.signalProxy.recordStateChanged.emit(state)

    @trace
    @pyqtSlot()
    def next_(self):
        self.connector.next_()
        self.lastCmdWasStep = True

    @trace
    @pyqtSlot()
    def reverse_next(self):
        self.connector.next_(True)
        self.lastCmdWasStep = True

    @trace
    @pyqtSlot()
    def step(self):
        self.connector.step()
        self.lastCmdWasStep = True

    @trace
    @pyqtSlot()
    def reverse_step(self):
        self.connector.step(True)
        self.lastCmdWasStep = True

    @trace
    @pyqtSlot()
    def cont(self):
        self.connector.cont()
        self.lastCmdWasStep = False

    @trace
    @pyqtSlot()
    def interrupt(self):
        self.connector.interrupt()
        self.lastCmdWasStep = False

    @trace
    @pyqtSlot()
    def finish(self):
        self.connector.finish()
        self.lastCmdWasStep = False

    @trace
    @pyqtSlot()
    def reverse_finish(self):
        self.connector.finish(True)
        self.lastCmdWasStep = False

    @pyqtSlot(str)
    def evaluateExpression(self, exp):
        if exp == "":
            return None
        exp = str(exp).replace('"', '\"')
        return self.connector.evaluate("\"" + exp + "\"")

    @trace
    @pyqtSlot(str)
    def executeCliCommand(self, cmd):
        return self.connector.executeCliCommand(cmd)

    def handleAsyncRecord(self, rec):
        if rec.type_ == GdbOutput.EXEC_ASYN and rec.class_ == GdbOutput.STOPPED:
            self.handleStoppedRecord(rec)
        elif rec.type_ == GdbOutput.EXEC_ASYN and rec.class_ == GdbOutput.RUNNING:
            self.signalProxy.inferiorIsRunning.emit(rec)
        elif rec.type_ == GdbOutput.NOTIFY_ASYN and rec.class_ == GdbOutput.THREAD_CREATED:
            self.signalProxy.threadCreated.emit(rec)
        elif rec.type_ == GdbOutput.NOTIFY_ASYN and rec.class_ == GdbOutput.THREAD_EXITED:
            self.signalProxy.threadExited.emit(rec)
        elif rec.type_ == GdbOutput.NOTIFY_ASYN and rec.class_ == GdbOutput.BREAKPOINT_MODIFIED:
            self.signalProxy.breakpointModified.emit(rec)

    def handleStoppedRecord(self, rec):
        # With reverse debugging, some stopped records might not contain a
        # reason. Predefine it as str(), since all unknown reasons will be
        # handled as the inferior having stopped normally.
        fields = ["reason", "frame", "signal-name", "signal-meaning", "bkptno", "wpt", "value"]
        field = defaultdict(str)

        for r in rec.results:
            if r.dest in fields:
                field[r.dest] = r.src

        if field["reason"] in ['exited-normally', 'exited']:
            self.signalProxy.inferiorHasExited.emit(rec)
        elif field["reason"] == 'breakpoint-hit':
            # Ok, we're kind of frantically trying to cover all bases here. We
            # cannot simply check for file:line combination reported in the
            # stopped message, since breakpoints may be set to a certain line
            # (which GDB also reports back as the line where the breakpoint is
            # really located), but one of the following lines may be reported in
            # the stopped message (eg., if the breakpoint is set to a function
            # header, the line reported here will be the first line of the
            # function's body).

            # Therefore, we're checking what was hit using the reported
            # breakpoint number. However, if the user sets both a breakpoint and
            # a tracepoint in the same line, only one number will be reported
            # here, but we need to handle both. Therefore, check the location
            # where what we found was supposed to be, and check if something
            # else was supposed to be there too. This still might be a problem
            # (eg. setting a breakpoint and a tracepoint in the line following
            # the breakpoint, both of which would cause the program to suspend
            # on yet another line), but that's about as good as our guessing
            # currently gets.
            p = self.do.tracepointController.model().breakpointByNumber(int(field["bkptno"])) or self.do.breakpointModel.breakpointByNumber(int(field["bkptno"]))  # either a TP or a BP must have been hit

            # now that we have one, check if others are here too
            tps = self.do.tracepointController.model().breakpointsByLocation(p.fullname, p.line)
            bps = self.do.breakpointModel.breakpointsByLocation(p.fullname, p.line)

            # before any breakpoint actions are executed, make sure all tracepoints gather their data
            if tps:
                # this will cause the variable pool to update all variables
                self.do.signalProxy.tracepointOccurred.emit()
                for i in tps:
                    i.recordData()

            for i in bps:
                if i.action:
                    self.do.scriptEnv.exec_(i.action)

            # if the last command was a step or any breakpoint tells us to not auto-continue, stop here
            if self.lastCmdWasStep or any(not p.autoContinue for p in itertools.chain(bps, tps)):
                self.signalProxy.inferiorStoppedNormally.emit(rec)
                self.lastCmdWasStep = False
            else:
                self.connector.cont()
        elif field["reason"] == "signal-received":
            logging.warning("Inferior received signal <b>%s</b> (%s) at <b>%s:%s</b>.", field["signal-name"], field["signal-meaning"], field["frame"].file, field["frame"].line)
            self.signalProxy.inferiorReceivedSignal.emit(rec)
        elif field["reason"] == "watchpoint-trigger":
            logging.warning("Watchpoint %s on expression <b>%s</b> triggered; old value: %s, new value: %s.", field["wpt"].number, self.do.breakpointModel.breakpointByNumber(field["wpt"].number).where, field["value"].old, field["value"].new)
            self.signalProxy.inferiorStoppedNormally.emit(rec)
        else:
            self.signalProxy.inferiorStoppedNormally.emit(rec)

    @trace
    @pyqtSlot()
    def inferiorUntil(self):
        file_, line = self.do.editorController.getCursorPosition()
        self.connector.until(file_, line)
        self.lastCmdWasStep = False

    def getExecutableName(self):
        return self.executableName

    @trace
    @pyqtSlot()
    def getStackDepth(self):
        return self.connector.getStackDepth()

    @trace
    @pyqtSlot()
    def selectStackFrame(self, exp):
        return self.connector.selectStackFrame(exp)
