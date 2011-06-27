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
from PyQt4.QtCore import QObject, SIGNAL, Qt, QSettings
from ptyhandler import PtyHandler
from gdboutput import GdbOutput

class DebugController(QObject):
    
    def __init__(self, distributed_objects):
        QObject.__init__(self)
        self.settings = QSettings("fh-hagenberg", "SysCDbg")
        self.ptyhandler = PtyHandler()
        
        self.distributed_objects = distributed_objects
        
        self.connector = self.distributed_objects.gdb_connector
        self.editor_controller = self.distributed_objects.editor_controller
        self.breakpoint_controller = self.distributed_objects.breakpoint_controller
        self.signalProxy = self.distributed_objects.signal_proxy
        
        self.executableName = None
        self.lastCmdWasStep = False
        
        self.ptyhandler.start()
        self.connector.start()

        QObject.connect(self.connector.reader, SIGNAL('asyncRecordReceived(PyQt_PyObject)'), self.handleAsyncRecord, Qt.QueuedConnection)
    
    def openExecutable(self, filename):
        if (self.editor_controller.closeOpenedFiles() == True): #closing source files may be canceled by user
            
            if self.executableName != None:
                #clear variables, tracepoints, watches,... by connecting to this signal
                self.signalProxy.emitCleanupModels()           
                                     
            self.connector.changeWorkingDirectory(os.path.dirname(filename))
            self.connector.openFile(filename)
            self.emit(SIGNAL('executableOpened'), filename)
            self.executableName = filename

    def run(self):
        self.connector.setTty(self.ptyhandler.ptyname)
        self.connector.run()
        self.lastCmdWasStep = False 
        self.signalProxy.emitRunClicked()
    
    def next_(self):
        self.connector.next_()
        self.lastCmdWasStep = True
    
    def step(self):
        self.connector.step()
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
    
    def evaluateExpression(self, exp):
        if exp == "":
            return None
        return self.connector.evaluate("\"" + exp + "\"")
    
    def executeCliCommand(self, cmd):
        return self.connector.executeCliCommand(cmd)

    def handleAsyncRecord(self, rec):
        if rec.type_ == GdbOutput.EXEC_ASYN:
            if rec.class_ == GdbOutput.STOPPED:
                self.handleStoppedRecord(rec)
            elif rec.class_ == GdbOutput.RUNNING:
                self.signalProxy.emitInferiorIsRunning(rec)

    def handleStoppedRecord(self, rec):
        for r in rec.results:
            if r.dest == 'reason':
                reason = r.src
            if r.dest == 'frame':
                frame = r.src
                
        if reason != 'exited-normally':
            stop = False
                        
            if reason == 'breakpoint-hit':    
                tp = self.distributed_objects.tracepoint_controller.tracepointModel.getTracepointIfAvailable(frame)
                
                if self.distributed_objects.breakpoint_controller.breakpointModel.isBreakpoint(frame) or self.lastCmdWasStep:
                    self.signalProxy.emitInferiorHasStopped(rec)
                    stop = True
                    self.lastCmdWasStep = False
                if tp != None:
                    tp.tracePointOccurred(stop)
                    self.distributed_objects.signal_proxy.emitTracepointOccurred()
            else:
                self.signalProxy.emitInferiorHasStopped(rec)                                
        else:
            self.signalProxy.emitInferiorHasExited(rec)

    def executePythonCode(self, code):
        exec(code)
    
    def inferiorUntil(self):
        current_opened_file = self.editor_controller.editor_view.getCurrentOpenedFile()
        line, col = current_opened_file.edit.getCursorPosition()        
        self.until(current_opened_file.filename, line+1)
    
    def getExecutableName(self):
        return self.executableName
    
    def getStackDepth(self):
        return self.connector.getStackDepth()
    
    def selectStackFrame(self, exp):
        return self.connector.selectStackFrame(exp)
        

