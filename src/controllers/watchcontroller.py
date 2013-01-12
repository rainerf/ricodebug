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
from helpers.icons import Icons
from helpers.excep import VariableNotFoundException
from models.variablemodel import VariableModel
from .treeitemcontroller import TreeItemController


class WatchController(TreeItemController):
    """ the Controller for the WatchView """

    def __init__(self, distributedObjects, view):
        """ Constructor <br>
            Create a WatchView, a WatchVWFactory and a VariableList <br>
            Listens to the following Signals: SignalProxy::AddWatch(QString), SignalProxy::insertDockWidgets() and SignalProxy::cleanupModels()
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        TreeItemController.__init__(self, distributedObjects, "Watch", view, VariableModel, True, Icons.watch)
        self.distributedObjects.signalProxy.AddWatch.connect(self.addWatch)

    def removeSelected(self, index):
        """ remove selected variable from WatchView
        @param row     int, selected row
        @param parent  TreeItem, parent item from selectected item
        """
        if not index.isValid():
            return
        vw = index.internalPointer()
        vw.dataChanged.disconnect(vw.hasChanged)
        self.variableList.removeVar(vw)
        self.model.removeRow(index.row(), index.parent())
        self.model.update()

    def addWatch(self, watch):
        """ adds the Variable watch to the VariableList and its wrapper to the WatchView
            this function is connected to the signal SignalProxy::AddWatch(QString)
        @param watch    Variable, the Variable to add to watch
        """
        try:
            vw = self.variableList.addVarByName(watch)
            vw.dataChanged.connect(vw.hasChanged)
            self.add(vw)
        except VariableNotFoundException:
            pass

    def saveSession(self, xmlHandler):
        """ Insert session info to xml file
        @param xmlHandler    sessionmanager.XmlHandler, handler to write to the session-xml-file
        """
        watchParent = xmlHandler.createNode("Watches")
        for var in self.variableModel.getVariables():
            xmlHandler.createNode("Watch", watchParent, {'exp': var.exp})

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
