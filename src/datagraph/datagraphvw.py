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

from PyQt4.QtCore import QObject, SIGNAL
from variables.variablewrapper import VariableWrapper
from htmlvariableview import HtmlVariableView
from PyQt4 import QtCore, QtGui

class HtmlTemplateHandler(QObject):
    """ Parent of all TemplateHandler-Classes. <br>
    renders the htmlTemplate and handles linkClicked-Events
    """
    
    def __init__(self, varWrapper, distributedObjects):
        """ Constructor
        @param varWrapper    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        QObject.__init__(self)
        self.varWrapper = varWrapper
        self.distributedObjects = distributedObjects
        self.htmlTemplate = None
        self.id = None              # our unique id which we can use inside the rendered HTML/JS
    
    def render(self, top, **kwargs):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        assert self.htmlTemplate != None
        assert self.varWrapper.getView()
        
        if not self.id:
            self.id = self.varWrapper.getView().getUniqueId(self)
        
        return self.htmlTemplate.render(varWrapper=self.varWrapper, top=top, id=self.id, **kwargs)
    
    @QtCore.pyqtSlot()
    def openContextMenu(self):
        self.varWrapper.openContextMenu()
    
    def prepareContextMenu(self, menu):
        pass
    
    @QtCore.pyqtSlot()
    def remove(self):
        self.distributedObjects.datagraph_controller.removeVar(self.varWrapper)

class DataGraphVW(VariableWrapper):
    """ Parent of all VariableWrappers for the DataGraph. <br>
        Specifies all important Functions for a VariableWrapper needed in the DataGraph-Module.
    """
    
    def __init__(self, variable, distributedObjects):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        VariableWrapper.__init__(self, variable)
        self.distributedObjects = distributedObjects
        self._view = None
        self.templateHandler = None
        self.parentWrapper = None
        
        self.dirty = True           # true if we need to rerender our stuff
        self.connect(self, SIGNAL('changed()'), self.setDirty)
        
        self.source = ""
    
    def createView(self):
        self._view = HtmlVariableView(self, self.distributedObjects)
        self.parentWrapper = self._view
    
    def setExistingView(self, view, parentWrapper):
        self._view = view
        self.parentWrapper = parentWrapper
    
    def getView(self):
        """ returns the view of the Variable
        @return    datagraph.htmlvariableview.HtmlVariableView, the view of the Variable """
        return self._view
    
    def openContextMenu(self, menu=None):
        if not menu:
            menu = QtGui.QMenu()
        self.templateHandler.prepareContextMenu(menu)
        self.parentWrapper.openContextMenu(menu)
    
    def changeTemplateHandler(self, type_):
        self.templateHandler = type_(self, self.distributedObjects)
        self.setDirty()
    
    @QtCore.pyqtSlot()
    def setDirty(self):
        self.dirty = True
        if self.parentWrapper:
            self.parentWrapper.setDirty()
    
    def getXPos(self):
        return self.getView().x()
    
    def setXPos(self, xPos):
        self.getView().setX(xPos)
    
    def getYPos(self):
        return self.getView().y()
    
    def setYPos(self, yPos):
        self.getView().setY(yPos)
    
    def render(self, top, **kwargs):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        if self.dirty:
            self.dirty = False
            self.source = self.templateHandler.render(top, **kwargs)
        return self.source
    
    def destroy(self):
        """ removes itself from the DataGraph """
        self.distributedObjects.datagraph_controller.removeVar(self)

