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


class SignalProxy(QObject):
    '''
    class presenting signal interface for plugins
    plugins only need this class to communicate with main program
    '''

    insertDockWidgets = pyqtSignal()
    removeDockWidget = pyqtSignal('QDockWidget')
    addDockWidget = pyqtSignal('PyQt_PyObject', 'QDockWidget', 'PyQt_PyObject')
    variableUpdateCompleted = pyqtSignal()
    registerWithSessionManager = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    runClicked = pyqtSignal()
    cleanupModels = pyqtSignal()
    saveFile = pyqtSignal()
    dataForTracepointsReady = pyqtSignal()
    tracepointOccurred = pyqtSignal()
    fileModified = pyqtSignal('PyQt_PyObject', bool)
    inferiorHasExited = pyqtSignal('PyQt_PyObject')
    inferiorReceivedSignal = pyqtSignal('PyQt_PyObject')
    inferiorStoppedNormally = pyqtSignal('PyQt_PyObject')
    inferiorIsRunning = pyqtSignal('PyQt_PyObject')
    executableOpened = pyqtSignal('PyQt_PyObject')
    AddWatch = pyqtSignal('PyQt_PyObject')
#    self.floatingWatchAdded.emit(watch)
#    self.fixedWatchAdded.emit(watch)


    def __init__(self, distributedObjects):
        '''CTOR'''
        QObject.__init__(self)
        self.distributedObjects = distributedObjects

    ###################################################
    # passing on signals
    ###################################################
    """ ============================================  WATCH  ============================================ """
    #def addWatchFixed(self, watch):
    #    self.fixedWatchAdded.emit(watch)

    #def addWatchFloating(self, watch):
    #    self.floatingWatchAdded.emit(watch)

    def addWatch(self, watch):
        self.AddWatch.emit(str(watch))
    """ ================================================================================================= """

    def emitExecutableOpened(self, filename):
        '''SLOT is called from signal of main program and passes another signal on to plugins'''
        self.executableOpened.emit(filename)

    def emitInferiorIsRunning(self, rec):
        self.inferiorIsRunning.emit(rec)

    def emitInferiorStoppedNormally(self, rec):
        self.inferiorStoppedNormally.emit(rec)

    def emitInferiorReceivedSignal(self, rec):
        self.inferiorReceivedSignal.emit(rec)

    def emitInferiorHasExited(self, rec):
        self.inferiorHasExited.emit(rec)

    def emitFileModified(self, filename, changed):
        '''Emit signal to mark a file as edited
        @param filename: string with path to file
        @param changed: True -> file has changed
        '''
        self.fileModified.emit(filename, changed)

    def emitTracepointOccurred(self):
        self.tracepointOccurred.emit()

    def emitDataForTracepointsReady(self):
        self.dataForTracepointsReady.emit()

    def emitSaveCurrentFile(self):
        '''Tell editorview to save current file'''
        self.saveFile.emit()

    def emitCleanupModels(self):
        '''Signal is emitted just before a new executable is opened to delete breakpoints, watches, ...'''
        self.cleanupModels.emit()

    def emitRunClicked(self):
        '''Signal is emitted after run button was clicked. '''
        self.runClicked.emit()

    def emitRegisterWithSessionManager(self, regObject, dialogItem):
        '''Register with session manager to add debug info to xml session file
            @param regObject: object must implement saveSession(self, XmlHandler) and loadSession(self, XmlHandler)
            @param dialogItem: String which appears with a checkbox in the save session dialog
        '''
        self.registerWithSessionManager.emit(regObject, dialogItem)

    def emitVariableUpdateCompleted(self):
        """Emitted when the variable pool has finished updating all variables
        for this step. Use this signal instead of rerendering stuff on the
        variable's changed() event to avoid multiple renderings."""
        self.variableUpdateCompleted.emit()

    # pass on further signals here ...

    ###################################################
    # functions for plugin placement in the mainwindow
    ###################################################
    def emitAddDockWidget(self, area, widget, addToggleViewAction=False):
        '''
        Emitting signal to tell mainwindow where to add a widget
        @param addToggleViewAction: True -> add the widget's toggleViewAction to the Menu
        '''
        self.addDockWidget.emit(area, widget, addToggleViewAction)

    def emitRemoveDockWidget(self, widget):
        '''Emitting signal to tell mainwindow where to add a widget '''
        self.removeDockWidget.emit(widget)

    def emitInsertDockWidgets(self):
        '''Emitting signal to tell controllers to insert their dock widgets '''
        self.insertDockWidgets.emit()

    # define further widget placement functions here ...

    ###################################################
    # functions for variable operations
    ###################################################

    def getVariable(self, exp):
        return self.distributedObjects.variablePool.getVar(str(exp))

    def getVariableChildren(self, name, childList, access):
        self.distributedObjects.variablePool.getChildren(name, childList, access)

    def getStlVectorSize(self, vector):
        return self.distributedObjects.stlvectorParser.getSize(vector)

    def getStlVectorContent(self, vector):
        return self.distributedObjects.stlvectorParser.getContent(vector)

    def openFile(self, file_, line):
        self.distributedObjects.editorController.jumpToLine(file_, line)

    # define further variable operation functions here ...

    ###################################################
    # functions for GDB commands
    ###################################################

    def gdbEvaluateExpression(self, exp):
        return self.distributedObjects.debugController.evaluateExpression(exp)

    def gdbGetStackDepth(self):
        return self.distributedObjects.debugController.getStackDepth()

    def gdbSelectStackFrame(self, nr):
        return self.distributedObjects.debugController.selectStackFrame(nr)

    # define further GDB command functions here ...
