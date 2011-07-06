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
from datagraph.datagraphvw import DataGraphVW, HtmlTemplateHandler
import sys
from PyQt4 import QtCore

class StructVariableTemplateHandler(HtmlTemplateHandler):
    """ TemplateHandler for Struct-Variables """
    
    def __init__(self, varWrapper, distributedObjects):
        """ Constructor
        @param varWrapper    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        HtmlTemplateHandler.__init__(self, varWrapper, distributedObjects)
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/structvariableview.mako')
    
    @QtCore.pyqtSlot()
    def open(self):
        self.varWrapper.setOpen(True)
    
    @QtCore.pyqtSlot()
    def close(self):
        self.varWrapper.setOpen(False)
    
    @QtCore.pyqtSlot()
    def graphicalView(self):
        self.varWrapper.changeTemplateHandler(ArrayTemplateHandler)
    
    def prepareContextMenu(self, menu):
        HtmlTemplateHandler.prepareContextMenu(self, menu)
        if self.varWrapper.isOpen:
            menu.addAction("Close %s" % self.varWrapper.getExp(), self.close)
        else:
            menu.addAction("Open %s" % self.varWrapper.getExp(), self.open)
        menu.addAction("Show %s graphically" % self.varWrapper.getExp(), self.graphicalView)

class StructDataGraphVW(DataGraphVW):
    """ VariableWrapper for Struct-Variables """
    
    def __init__(self, variable, distributedObjects, vwFactory):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        DataGraphVW.__init__(self, variable, distributedObjects)
        self.isOpen = True
        self.vwFactory = vwFactory
        self.children = None        # will be lazily evaluated once we need them
        self.templateHandler = StructVariableTemplateHandler(self, self.distributedObjects)
    
    def setOpen(self, open):
        self.isOpen = open
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
    
class ArrayTemplateHandler(StructVariableTemplateHandler):
    """ TemplateHandler for graphical representation of arrays"""
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        StructVariableTemplateHandler.__init__(self, var, distributedObjects)
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/arrayview.mako')
        
    def render(self, top, **kwargs):
        data = [var.getValue() for var in self.varWrapper.children]
        return StructVariableTemplateHandler.render(self, top, data=data)
    
    @QtCore.pyqtSlot()
    def stdView(self):
        self.varWrapper.changeTemplateHandler(StructVariableTemplateHandler)

    def prepareContextMenu(self, menu):
        menu.addAction("Change to std view for %s" % self.varWrapper.getExp(), self.stdView)
