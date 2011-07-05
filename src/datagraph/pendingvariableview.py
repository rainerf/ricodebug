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

from datagraphvw import DataGraphVW, HtmlTemplateHandler

class PendingVariableTemplateHandler(HtmlTemplateHandler):
    """ TemplateHandler for pending Variables """
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        HtmlTemplateHandler.__init__(self, var, distributedObjects)
    
    def execLinkCommand(self, commandStr, mainView):
        """ handles the given Command
        @param commandStr  String, the Command to handle
        @param mainView    datagraph.datagraphvw.HtmlVariableView, the View of the top-level-Variable """
        pass
    
    def render(self, handlers, view):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        # do not render anything for PendingVar
        #return "pending: " + self.var.getExp()
        return ""
    

class PendingDataGraphVW(DataGraphVW):
    """ VariableWrapper for pending Variables """
    
    def __init__(self, variable, distributedObjects):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        DataGraphVW.__init__(self, variable, distributedObjects)
        self.templateHandler = PendingVariableTemplateHandler(self, self.distributedObjects)
