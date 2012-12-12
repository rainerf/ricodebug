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
from helpers.ptyhandler import PtyHandler
from PyQt4.QtCore import QObject, pyqtSignal, Qt, pyqtSlot
from helpers.gdboutput import GdbOutput
import logging
from helpers.configstore import ConfigSet, ConfigItem


class DebugConfig(ConfigSet):
    def __init__(self):
        ConfigSet.__init__(self, "Debugging", "Debugging Options")
        self.breakAtMain = ConfigItem(self, "Break at main function", True)


class DebugController(QObject):
    executableOpened = pyqtSignal('PyQt_PyObject')

    def __init__(self, distributedObjects):
        QObject.__init__(self)

        self.ptyhandler = PtyHandler()

        self.distributedObjects = distributedObjects

        self.connector = self.distributedObjects.gdb_connector
        self.gdbinit = self.distributedObjects.gdb_init
        self.signalProxy = self.distributedObjects.signalProxy

        self.executableName = None
        self.lastCmdWasStep = False

        self.ptyhandler.start()
        
        self.gdbinit.writeFile()
        
        self.connector.start()
        
        self.connector.initPrettyPrinter(self.gdbinit.getPath())
        self.connector.startPrettyPrinting()
        
        self.toggleBeautify = True

        self.connector.reader.asyncRecordReceived.connect(self.handleAsyncRecord, Qt.QueuedConnection)

        self.__config = DebugConfig()
        self.distributedObjects.configStore.registerConfigSet(self.__config)
        self.__config.itemsHaveChanged.connect(self.updateConfig)

    def updateConfig(self):
        if self.executableName:
            logging.warning("Please reload executable for changes to take effect!")

    def openExecutable(self, filename):
        # make sure we only open absolute paths, otherwise eg. RecentFileHandler
        # will not know _where_ the file was we opened and store different
        # relative paths for the same file
        filename = os.path.abspath(filename)

        if not os.path.exists(filename):
            logging.error("File %s was not found.", filename)
            return

        if self.distributedObjects.editorController.closeOpenedFiles():  # closing source files may be canceled by user
            if self.executableName != None:
                #clear variables, tracepoints, watches,... by connecting to this signal
                self.signalProxy.emitCleanupModels()

            self.connector.changeWorkingDirectory(os.path.dirname(filename))
            self.connector.openFile(filename)
            if self.__config.breakAtMain.value:
                self.distributedObjects.breakpointModel.insertBreakpoint("main", None)
            self.executableOpened.emit(filename)
            self.executableName = filename

    def run(self, args=None):
        self.connector.setTty(self.ptyhandler.ptyname)
        self.connector.setArgs(args)
        self.connector.run()
        self.lastCmdWasStep = False
        self.signalProxy.emitRunClicked()

    def record_start(self):
        self.connector.record_start()

    def record_stop(self):
        self.connector.record_stop()

    def next_(self):
        self.connector.next_()
        self.lastCmdWasStep = True

    def reverse_next(self):
        self.connector.reverse_next()
        self.lastCmdWasStep = True

    def step(self):
        self.connector.step()
        self.lastCmdWasStep = True

    def reverse_step(self):
        self.connector.reverse_step()
        self.lastCmdWasStep = True

    def cont(self):
        self.connector.cont()
        self.lastCmdWasStep = False

    def interrupt(self):
        self.connector.interrupt()
        self.lastCmdWasStep = False

    def finish(self):
        self.connector.finish()
        self.lastCmdWasStep = False

    def until(self, file_, line):
        self.connector.until(file_, line)
        self.lastCmdWasStep = False
        
    def beautify(self):
        if self.toggleBeautify:
            self.connector.disablePrettyPrinter()
        else:
            self.connector.enablePrettyPrinter()
        
        self.toggleBeautify = not self.toggleBeautify
        self.distributedObjects.localsController.reloadLocals()

    def evaluateExpression(self, exp):
        if exp == "":
            return None
        exp = exp.replace('"', '\"')
        return self.connector.evaluate("\"" + exp + "\"")

    def executeCliCommand(self, cmd):
        return self.connector.executeCliCommand(cmd)

    def handleAsyncRecord(self, rec):
        if rec.type_ == GdbOutput.EXEC_ASYN:
            if rec.class_ == GdbOutput.STOPPED:
                self.handleStoppedRecord(rec)
            elif rec.class_ == GdbOutput.RUNNING:
                self.signalProxy.emitInferiorIsRunning(rec)
        elif rec.type_ == GdbOutput.NOTIFY_ASYN:
            if rec.class_ == GdbOutput.THREAD_CREATED:
                self.signalProxy.emitThreadCreated(rec)
            elif rec.class_ == GdbOutput.THREAD_EXITED:
                self.signalProxy.emitThreadExited(rec)

    def handleStoppedRecord(self, rec):
        # With reverse debugging, some stopped records might not contain a
        # reason. Predefine it as None, since all unknown reasons will be
        # handled as the inferior having stopped normally.
        reason = None

        for r in rec.results:
            if r.dest == 'reason':
                reason = r.src
            if r.dest == 'frame':
                frame = r.src
            if r.dest == 'signal-name':
                signal_name = r.src
            if r.dest == 'signal-meaning':
                signal_meaning = r.src
            if r.dest == "bkptno":
                bkptno = int(r.src)

        if reason in ['exited-normally', 'exited']:
            self.signalProxy.emitInferiorHasExited(rec)
        elif reason == 'breakpoint-hit':
                stop = False
                tp = self.distributedObjects.tracepointController.model().getTracepointIfAvailable(frame)

                if self.distributedObjects.breakpointModel.isBreakpointByNumber(bkptno) or self.lastCmdWasStep:
                    self.signalProxy.emitInferiorStoppedNormally(rec)
                    stop = True
                    self.lastCmdWasStep = False
                if tp != None:
                    tp.tracePointOccurred(stop)
                    self.distributedObjects.signalProxy.emitTracepointOccurred()
        elif reason == "signal-received":
            logging.warning("Signal received: %s (%s) in %s:%s", signal_name, signal_meaning, frame.file, frame.line)
            self.signalProxy.emitInferiorReceivedSignal(rec)
        else:
            self.signalProxy.emitInferiorStoppedNormally(rec)

    def executePythonCode(self, code):
        exec(code, {'do': self.distributedObjects})

    def inferiorUntil(self):
        current_opened_file = self.distributedObjects.editorController.editor_view.getCurrentOpenedFile()
        line, _ = current_opened_file.edit.getCursorPosition()
        self.until(current_opened_file.filename, line + 1)

    def getExecutableName(self):
        return self.executableName

    def getStackDepth(self):
        return self.connector.getStackDepth()

    def selectStackFrame(self, exp):
        return self.connector.selectStackFrame(exp)
