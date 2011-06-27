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

class StructVariableTemplateHandler(HtmlTemplateHandler):
    """ TemplateHandler for Struct-Variables """
    
    def __init__(self, var):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        HtmlTemplateHandler.__init__(self, var)
        self.var = var
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/structvariableview.mako')
    
    def execLinkCommand(self, commandStr, mainView):
        """ handles the given Command
        @param commandStr  String, the Command to handle
        @param mainView    datagraph.datagraphvw.HtmlVariableView, the View of the top-level-Variable """
        if (commandStr == "remove"):
            print "... removing ptrvariableview ..."
            self.var.destroy()
        if (commandStr == "open"):
            self.var.isOpen = True
        if (commandStr == "close"):
            self.var.isOpen = False
    


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
    
    def getTemplateHandler(self):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        if (self.templateHandler == None):
            self.templateHandler = StructVariableTemplateHandler(self)
        return self.templateHandler
    
    def getChildren(self):
        """ returns list of children as DataGraphVWs
        @return    list of datagraph.datagraphvw.DataGraphVW """
        children = []
        for childVar in self.variable.getChildren():
            children.append(childVar.makeWrapper(self.vwFactory))
        return children
    
