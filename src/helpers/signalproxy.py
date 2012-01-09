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

from PyQt4.QtCore import SIGNAL, QObject
'''
Created on Mar 9, 2011

@author: bschen
'''

class SignalProxy(QObject):
    '''
    class presenting signal interface for plugins
    plugins only need this class to communicate with main program
    '''
    
    def __init__(self, distributedObjects):
        '''CTOR'''
        QObject.__init__(self)
        self.distributedObjects = distributedObjects
    
    ###################################################
    # passing on signals  
    ###################################################    
    """ ============================================  WATCH  ============================================ """
    #def addWatchFixed(self, watch):
    #    self.emit(SIGNAL('fixedWatchAdded(QString)'), watch)
    
    #def addWatchFloating(self, watch):
    #    self.emit(SIGNAL('floatingWatchAdded(QString)'), watch)
        
    def addWatch(self, watch):
        self.emit(SIGNAL('AddWatch(QString)'), str(watch))
    """ ================================================================================================= """

    def emitExecutableOpened(self, filename):
        '''SLOT is called from signal of main program and passes another signal on to plugins'''
        self.emit(SIGNAL('executableOpened(QString)'), filename)
        
    def emitInferiorIsRunning(self, rec):
        self.emit(SIGNAL('inferiorIsRunning(PyQt_PyObject)'), rec)
    
    def emitInferiorStoppedNormally(self, rec):
        self.emit(SIGNAL('inferiorStoppedNormally(PyQt_PyObject)'), rec)
    
    def emitInferiorReceivedSignal(self, rec):
        self.emit(SIGNAL('inferiorReceivedSignal(PyQt_PyObject)'), rec)
        
    def emitInferiorHasExited(self, rec):
        self.emit(SIGNAL('inferiorHasExited(PyQt_PyObject)'), rec)
    
    def emitFileModified(self, filename, changed):
        '''Emit signal to mark a file as edited
        @param filename: string with path to file
        @param changed: True -> file has changed 
        '''
        self.emit(SIGNAL('fileModified(PyQt_PyObject, bool)'), filename, changed)
    
    def emitTracepointOccurred(self):
        self.emit(SIGNAL('tracepointOccurred()'))
        
    def emitDataForTracepointsReady(self):
        self.emit(SIGNAL('dataForTracepointsReady()'))
    
    def emitSaveCurrentFile(self):
        '''Tell editorview to save current file'''
        self.emit(SIGNAL('saveFile()'))

    def emitCleanupModels(self):
        '''Signal is emitted just before a new executable is opened to delete breakpoints, watches, ...'''
        self.emit(SIGNAL('cleanupModels()'))
        
    def emitRunClicked(self):
        '''Signal is emitted after run button was clicked. '''
        self.emit(SIGNAL('runClicked()'))
     
    def emitRegisterWithSessionManager(self, regObject, dialogItem):
        '''Register with session manager to add debug info to xml session file
            @param regObject: object must implement saveSession(self, XmlHandler) and loadSession(self, XmlHandler)
            @param dialogItem: String which appears with a checkbox in the save session dialog 
        '''
        self.emit(SIGNAL('registerWithSessionManager(PyQt_PyObject, PyQt_PyObject)'), regObject, dialogItem)

    def emitVariableUpdateCompleted(self):
        """Emitted when the variable pool has finished updating all variables
        for this step. Use this signal instead of rerendering stuff on the
        variable's changed() event to avoid multiple renderings."""
        self.emit(SIGNAL("variableUpdateCompleted()"))

    # pass on further signals here ...
    
    ###################################################
    # functions for plugin placement in the mainwindow
    ###################################################   
    def addDockWidget(self, area, widget, addToggleViewAction = False):
        '''Emitting signal to tell mainwindow where to add a widget 
			@param addToggleViewAction: True -> add the widget's toggleViewAction to the Menu
        '''
        self.emit(SIGNAL('addDockWidget(PyQt_PyObject, QDockWidget, PyQt_PyObject)'), area, widget, addToggleViewAction)
    
    def removeDockWidget(self, widget):
        '''Emitting signal to tell mainwindow where to add a widget '''
        self.emit(SIGNAL('removeDockWidget(QDockWidget)'), widget)
        
    def insertDockWidgets(self):
        '''Emitting signal to tell controllers to insert their dock widgets '''
        self.emit(SIGNAL('insertDockWidgets()'))

    # define further widget placement functions here ...
    
    ###################################################
    # functions for variable operations
    ###################################################
    
    def getVariable(self, exp):
        return self.distributedObjects.variable_pool.getVar(str(exp))
    
    def getVariableChildren(self, name, childList, access):
        self.distributedObjects.variable_pool.getChildren(name, childList, access)
    
    def getStlVectorSize(self, vector):
        return self.distributedObjects.stlvector_parser.getSize(vector)
    
    def getStlVectorContent(self, vector):
        return self.distributedObjects.stlvector_parser.getContent(vector)
    
    def openFile(self, file_, line):
        self.distributedObjects.editor_controller.jumpToLine(file_, line)
    
    # define further variable operation functions here ...
    
    ###################################################
    # functions for GDB commands
    ###################################################
        
    def gdbEvaluateExpression(self, exp):
        return self.distributedObjects.debug_controller.evaluateExpression(exp)
    
    def gdbGetStackDepth(self):
        return self.distributedObjects.debug_controller.getStackDepth()
    
    def gdbSelectStackFrame(self, nr):
        return self.distributedObjects.debug_controller.selectStackFrame(nr)
    
    # define further GDB command functions here ...
    
