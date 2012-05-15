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

""" @package controllers.watchcontroller    the WatchController """

from models.variablemodel import VariableModel
from views.watchview import WatchView
from treeitemcontroller import TreeItemController

#####################################################################################
## CONTROLLER
#####################################################################################


class WatchController(TreeItemController):
    """ the Controller for the WatchView """

    def __init__(self, distributedObjects):
        """ Constructor <br>
            Create a WatchView, a WatchVWFactory and a VariableList <br>
            Listens to the following Signals: SignalProxy::AddWatch(QString), SignalProxy::insertDockWidgets() and SignalProxy::cleanupModels()
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        TreeItemController.__init__(self, distributedObjects, "Watch", WatchView, VariableModel)
        self.distributedObjects.signalProxy.AddWatch.connect(self.addWatch)

    def removeSelected(self, row, parent):
        """ remove selected variable from WatchView
        @param row     int, selected row
        @param parent  TreeItem, parent item from selectected item
        """
        self.variableModel.removeRow(row, parent)

    def addWatch(self, watch):
        """ adds the Variable watch to the VariableList and its wrapper to the WatchView
            this function is connected to the signal SignalProxy::AddWatch(QString)
        @param watch    Variable, the Variable to add to watch
        """
        vw = self.variableList.addVarByName(watch)
        # connect changed and replace signal from wrapper
        vw.changed.connect(vw.hasChanged)
        vw.replace.connect(self.replaceVariable)

        self.add(vw)

    def replaceVariable(self, pendingVar, newVar):
        """ replaces a variable in the variablelist
        @param pendingVar    variables.variablewrapper.VariableWrapper, VariableWrapper to replace in the list
        @param newVar        variables.Variable, new Variable which replaces existing VariableWrapper in List
        """
        vwOld = self.variableList.getVariableWrapper(pendingVar)

        vwNew = self.variableList.replaceVar(pendingVar, newVar)
        vwNew.changed.connect(vwNew.hasChanged)
        vwNew.replace.connect(self.replaceVariable)

        # set parent for root variable
        vwNew.setParent(self.variableModel.root)

        # add variable to root children
        self.variableModel.root.replaceChild(vwOld, vwNew)

        vwNew.setChanged(True)
        self.variableModel.update()

    def saveSession(self, xmlHandler):
        """ Insert session info to xml file
        @param xmlHandler    sessionmanager.XmlHandler, handler to write to the session-xml-file
        """
        watchParent = xmlHandler.createNode("Watches")
        for var in self.variableModel.getVariables():
            xmlHandler.createNode("Watch", watchParent, {'exp': var.getExp()})

    def loadSession(self, xmlHandler):
        """ load session info to xml file
        @param xmlHandler    sessionmanager.XmlHandler, handler to read from the session-xml-file
        """
        watchParent = xmlHandler.getNode("Watches")
        if watchParent != None:
            childnodes = watchParent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self.addWatch(attr["exp"])
