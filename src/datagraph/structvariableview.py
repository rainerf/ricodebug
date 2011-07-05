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
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        HtmlTemplateHandler.__init__(self, var, distributedObjects)
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/structvariableview.mako')
    
    @QtCore.pyqtSlot()
    def open(self):
        self.var.isOpen = True
        self.setDirty()
    
    @QtCore.pyqtSlot()
    def close(self):
        self.var.isOpen = False
        self.setDirty()
#
#    @QtCore.pyqtSlot()
#    def graphicalView(self):
#        self.var.setTemplateHandler(ArrayTemplateHandler)

    def prepareContextMenu(self, menu):
        if self.var.isOpen:
            menu.addAction("Close %s" % self.var.variable.exp, self.close)
        else:
            menu.addAction("Open %s" % self.var.variable.exp, self.open)
#        menu.addAction("Change to graphical view for %s" % self.var.variable.exp, self.graphicalView)
        HtmlTemplateHandler.prepareContextMenu(self, menu)

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
        self.children = None
        self.templateHandler = StructVariableTemplateHandler(self, self.distributedObjects)
    
    def getChildren(self):
        """ returns list of children as DataGraphVWs
        @return    list of datagraph.datagraphvw.DataGraphVW """
        if not self.children:
            self.children = []
            for childVar in self.variable.getChildren():
                self.children.append(childVar.makeWrapper(self.vwFactory))
        return self.children
    
    def setTemplateHandler(self, type_):
        oldParentHandler = self.templateHandler.parentHandler
        self.templateHandler = type_(self, self.distributedObjects)
        self.templateHandler.parentHandler = oldParentHandler 
        self.templateHandler.setDirty()

#class ArrayTemplateHandler(StructVariableTemplateHandler):
#    """ TemplateHandler for graphical representation of arrays"""
#    
#    def __init__(self, var, distributedObjects):
#        """ Constructor
#        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
#        StructVariableTemplateHandler.__init__(self, var, distributedObjects)
#        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/arrayview.mako')
#        self.data = []
#        
#        for var in self.var.children:
#            self.connect(var, QtCore.SIGNAL('changed()'), self.setDirty)
#        
#    def render(self, view, top, parentHandler, **kwargs):
#        data= [var.variable.value for var in self.var.children]
#        return StructVariableTemplateHandler.render(self, view, top, parentHandler, data=data)
#    
#    @QtCore.pyqtSlot()
#    def stdView(self):
#        self.var.setTemplateHandler(StructVariableTemplateHandler)
#
#    def prepareContextMenu(self, menu):
#        if self.var.isOpen:
#            menu.addAction("Change to std view for %s" % self.var.variable.exp, self.stdView)
#        StructVariableTemplateHandler.prepareContextMenu(self, menu)
#
#    def setDirty(self):
#        print "i'm dirty"
#        StructVariableTemplateHandler.setDirty(self)
