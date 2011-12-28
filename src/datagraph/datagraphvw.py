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

from mako.template import Template
from mako.lookup import TemplateLookup
import sys
from PyQt4.QtCore import QObject, SIGNAL
from variables.variablewrapper import VariableWrapper
from htmlvariableview import HtmlVariableView
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidgetAction, QLabel, QIcon

class Role:
    NORMAL, INCLUDE_HEADER, VALUE_ONLY= range(3)

class HtmlTemplateHandler(QObject):
    """ Parent of all TemplateHandler-Classes. <br>
    renders the htmlTemplate and handles linkClicked-Events
    """
    
    def __init__(self, varWrapper, distributedObjects, template):
        """ Constructor
        @param varWrapper    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        QObject.__init__(self)
        self.varWrapper = varWrapper
        self.distributedObjects = distributedObjects
        self.id = None              # our unique id which we can use inside the rendered HTML/JS
        
        self._templateLookup = TemplateLookup(directories=[sys.path[0] + "/datagraph/templates/"])
        
        self._htmlTemplate = None
        self.setTemplate(template)
    
    def setTemplate(self, template):
        self._htmlTemplate = Template(filename=sys.path[0] + "/datagraph/templates/" + template, lookup=self._templateLookup)
    
    def render(self, role, **kwargs):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        assert self._htmlTemplate != None
        assert self.varWrapper.getView()
        
        if not self.id:
            self.id = self.varWrapper.getView().getUniqueId(self)
        
        return self._htmlTemplate.render(varWrapper=self.varWrapper, role=role, id=self.id, **kwargs)
    
    @QtCore.pyqtSlot()
    def openContextMenu(self):
        self.varWrapper.openContextMenu()
    
    def prepareContextMenu(self, menu):
        menu.addSeparator()
        self.addContextMenuLabel(menu)
    
    # insert a "header" into the menu for the current element
    def addContextMenuLabel(self, menu):
        label = QLabel("Actions for %s" % (self.varWrapper.getExp()))
        label.setStyleSheet("color:palette(light); background-color:palette(dark); margin-top:2px; margin-bottom:2px; margin-left:2px; margin-right:2px;");
        we = QWidgetAction(menu)
        we.setDefaultWidget(label)
        menu.addAction(we)
    
    @QtCore.pyqtSlot()
    def remove(self):
        self.distributedObjects.datagraph_controller.removeVar(self.varWrapper)

class ComplexTemplateHandler(HtmlTemplateHandler):
    def __init__(self, varWrapper, distributedObjects, template):
        HtmlTemplateHandler.__init__(self, varWrapper, distributedObjects, template)
        self.vertical = True
    
    @QtCore.pyqtSlot()
    def toggleCollapsed(self):
        self.varWrapper.setOpen(not self.varWrapper.isOpen)
    
    @QtCore.pyqtSlot()
    def toggleVertical(self):
        self.vertical = not self.vertical
        
        # the way our children will be rendered will change too (include/skip
        # <tr> etc), so mark them as dirty, but do not force immediate rerendering;
        # this will be done when we mark ourselves as dirty
        for child in self.varWrapper.getChildren():
            child.setDirty(False)
        self.varWrapper.setDirty(True)
    
    def prepareContextMenu(self, menu):
        HtmlTemplateHandler.prepareContextMenu(self, menu)
        
        action = menu.addAction(QIcon(":/icons/images/collapse.png"), "Collapse %s" % self.varWrapper.getExp(), self.toggleCollapsed)
        action.setCheckable(True)
        action.setChecked(not self.varWrapper.isOpen)
        
        if self.varWrapper.isOpen:
            action = menu.addAction(QIcon(":/icons/images/vertical.png"), "Vertical view for %s" % self.varWrapper.getExp(), self.toggleVertical)
            action.setCheckable(True)
            action.setChecked(self.vertical)
    
    def render(self, role, **kwargs):
        return HtmlTemplateHandler.render(self, role, vertical=self.vertical, **kwargs)

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
        self.setDirty(True)
    
    @QtCore.pyqtSlot()
    def setDirty(self, render_immediately=False):
        self.dirty = True
        if self.parentWrapper:
            self.parentWrapper.setDirty(render_immediately)
    
    def getXPos(self):
        return self.getView().x()
    
    def setXPos(self, xPos):
        self.getView().setX(xPos)
    
    def getYPos(self):
        return self.getView().y()
    
    def setYPos(self, yPos):
        self.getView().setY(yPos)
    
    def render(self, role, **kwargs):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        if self.dirty:
            self.dirty = False
            self.source = self.templateHandler.render(role, **kwargs)
        return self.source
    
    def destroy(self):
        """ removes itself from the DataGraph """
        self.distributedObjects.datagraph_controller.removeVar(self)

    def setFilter(self, f):
        VariableWrapper.setFilter(self, f)
        self.setDirty(True)

class ComplexDataGraphVW(DataGraphVW):
    def __init__(self, variable, distributedObjects, vwFactory, templateHandler):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        DataGraphVW.__init__(self, variable, distributedObjects)
        self.isOpen = True
        self.vwFactory = vwFactory
        self.children = None        # will be lazily evaluated once we need them
        self.templateHandler = templateHandler
    
    def setOpen(self, open_):
        self.isOpen = open_
        self.setDirty(True)
    
    def getChildren(self):
        """ returns list of children as DataGraphVWs; creates the wrappers if they haven't yet been
        @return    list of datagraph.datagraphvw.DataGraphVW """
        if not self.children:
            self.children = []
            for childVar in self.variable.getChildren():
                wrapper = childVar.makeWrapper(self.vwFactory)
                wrapper.setExistingView(self.getView(), self)
                self.children.append(wrapper)
        return self.children
