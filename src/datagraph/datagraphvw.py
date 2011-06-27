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

from PyQt4.QtCore import QObject
from variables.variablewrapper import VariableWrapper
from htmlvariableview import HtmlVariableView

class HtmlTemplateHandler(QObject):
    """ Parent of all TemplateHandler-Classes. <br>
    renders the htmlTemplate and handles linkClicked-Events
    """
    
    def __init__(self, var):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        QObject.__init__(self)
        self.var = var
        self.htmlTemplate = None
    
    def render(self, handlers=None):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        assert(self.htmlTemplate != None)
        top = False
        if ((handlers == None) or (len(handlers) == 0)):
            top = True
        if ((handlers != None) and not(handlers.__contains__(self))):
            handlers.append(self)
        self.html = (self.htmlTemplate.render(var=self.var, handlers=handlers, top=top))
        return self.html
    
    def linkClicked(self, url, mainView):
        """ handles the Click-Event of a Link
        @param url         String, the clicked URL
        @param mainView    datagraph.datagraphvw.HtmlVariableView, the View of the top-level-Variable
        """
        urlStr = str(url.toString())
        print "HtmlTemplateHandler: link clicked: " + urlStr
        urlStrParts = urlStr.split(';')
        assert(len(urlStrParts) >= 2)
        #varStr = urlStrParts[0]
        commandStr = urlStrParts[1]
        self.execLinkCommand(commandStr, mainView)
    
    def execLinkCommand(self, commandStr, mainView):
        """ abstract method <br>
            handles the given Command
        @param commandStr  String, the Command to handle
        @param mainView    datagraph.datagraphvw.HtmlVariableView, the View of the top-level-Variable """
        raise "abstract method DataGraphVW.execLinkCommand() has been called."
    


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
        raise "abstract method DataGraphVW.getTemplateHandler() has been called."
    
    def destroy(self):
        """ removes itself from the DataGraph """
        self.distributedObjects.datagraph_controller.removeVar(self)

