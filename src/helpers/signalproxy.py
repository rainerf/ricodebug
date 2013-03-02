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
    addDockWidget = pyqtSignal('PyQt_PyObject', 'QDockWidget', 'PyQt_PyObject')
    variableUpdateCompleted = pyqtSignal()
    aboutToUpdateVariables = pyqtSignal()
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
    threadCreated = pyqtSignal('PyQt_PyObject')
    threadExited = pyqtSignal('PyQt_PyObject')
    AddWatch = pyqtSignal('PyQt_PyObject')
    breakpointModified = pyqtSignal('PyQt_PyObject')
    recordStateChanged = pyqtSignal(bool)

    def __init__(self, distributedObjects):
        QObject.__init__(self)
        self.distributedObjects = distributedObjects
        self.pluginDocks = {}
        self.pluginSbWidgets = {}

    def addWatch(self, watch):
        self.AddWatch.emit(str(watch))

    ###################################################
    # functions for plugin placement in the mainwindow
    ###################################################

    def insertDockWidget(self, plugin, widget, name, area, addToggleViewAction, icon=None):
        d = self.distributedObjects.mainwindow.insertDockWidget(widget, name, area, addToggleViewAction, icon)
        self.pluginDocks[plugin] = d

    def removeDockWidget(self, plugin):
        self.distributedObjects.mainwindow.removeDockWidget(self.pluginDocks[plugin])

    def insertStatusbarWidget(self, plugin, widget):
        d = self.distributedObjects.mainwindow.insertStatusbarWidget(widget)
        self.pluginSbWidgets[plugin] = d

    def removeStatusbarWidget(self, plugin):
        self.distributedObjects.mainwindow.removeStatusbarWidget(self.pluginSbWidgets[plugin])

    # define further widget placement functions here ...

    ###################################################
    # functions for variable operations
    ###################################################

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
