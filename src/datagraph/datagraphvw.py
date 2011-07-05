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
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        QObject.__init__(self)
        self.var = var
        self.distributedObjects = distributedObjects
        self.htmlTemplate = None
        self.view = None            # the HtmlVariableView that will contain what we render
        self.dirty = True           # true if we need to rerender our stuff
        self.id = None              # our unique id which we can use inside the rendered HTML/JS
        
        self.parentHandler = None
        self.source = ""
        
        self.connect(self.var, SIGNAL('changed()'), self.setDirty)
    
    def render(self, view, top, parentHandler, **kwargs):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        assert(self.htmlTemplate != None)
        self.parentHandler = parentHandler
        self.view = view
        
        if not self.id:
            self.id = view.getUniqueId(self)
        
        if self.dirty:
            self.source = self.htmlTemplate.render(var=self.var, view=view, top=top, parentHandler=self, id=self.id, **kwargs)
            self.dirty = False
        return self.source
    
    def setDirty(self):
        self.dirty = True
        if self.parentHandler:
            self.parentHandler.setDirty()

    @QtCore.pyqtSlot()
    def openContextMenu(self):
        menu = QtGui.QMenu()
        self.prepareContextMenu(menu)
        self.view.showContextMenu(menu)
    
    def prepareContextMenu(self, menu):
        self.parentHandler.prepareContextMenu(menu)
    
    @QtCore.pyqtSlot()
    def remove(self):
        self.distributedObjects.datagraph_controller.removeVar(self.var)

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
        self.view = None
        self.templateHandler = None
    
    def getView(self):
        """ returns the view of the Variable
        @return    datagraph.htmlvariableview.HtmlVariableView, the view of the Variable """
        if (self.view == None):
            self.view = HtmlVariableView(self, self.distributedObjects)
            self.view.setX(0)
            self.view.setY(0)
        return self.view
    
    def getXPos(self):
        return self.getView().x()
    
    def setXPos(self, xPos):
        self.getView().setX(xPos)
    
    def getYPos(self):
        return self.getView().y()
    
    def setYPos(self, yPos):
        self.getView().setY(yPos)
    
    def getTemplateHandler(self):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        return self.templateHandler
    
    def destroy(self):
        """ removes itself from the DataGraph """
        self.distributedObjects.datagraph_controller.removeVar(self)

