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
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QIcon

from helpers.excep import VariableNotFoundException
from .datagraphview import DataGraphView
from variables.variablelist import VariableList
from .pointer import Pointer
from .stdvariableview import DataGraphStdVariable
from .arrayvariableview import DataGraphArrayVariable
from .ptrvariableview import DataGraphPtrVariable
from .structvariableview import DataGraphStructVariable


class DataGraphVariableFactory:
    StdVariable = DataGraphStdVariable
    ArrayVariable = DataGraphArrayVariable
    PtrVariable = DataGraphPtrVariable
    StructVariable = DataGraphStructVariable


class DataGraphController(QObject):
    """ the Controller for the DataGraph """

    def __init__(self, distributedObjects):
        QObject.__init__(self)

        self.distributedObjects = distributedObjects
        self.signalProxy = distributedObjects.signalProxy

        self._view = DataGraphView(None)

        self.variableList = VariableList(DataGraphVariableFactory, self.distributedObjects)

        # register with session manager to save Graph
        self.signalProxy.emitRegisterWithSessionManager(self, "Graph")

        # connect signals
        self.signalProxy.cleanupModels.connect(self.clearDataGraph)

        self.distributedObjects.mainwindow.insertDockWidget(self._view, "Graph", Qt.LeftDockWidgetArea, True, QIcon(":/icons/images/datagraph.png"))

    def addWatch(self, watch, xPos=0, yPos=0):
        """ adds `watch' to the DataGraph
        @param watch    str, variable to add
        @param xPos     int, x coordinate of the desired position
        @param yPos     int, y coordinate of the desired position
        """
        try:
            var = self.variableList.addVarByName(watch)
            var.setData(self.distributedObjects)

            var.createView()
            var.getView().render()
            var.setXPos(xPos)
            var.setYPos(yPos)
            self._view.addItem(var.getView())

            return var
        except VariableNotFoundException:
            return None

    def addDereferencedPointer(self, source, name):
        target = self.addWatch(str(name))
        self.addPointer(source.getView(), target.getView())

    def removeVar(self, var):
        self.variableList.removeVar(var)
        self._view.removeItem(var.getView())

    def addPointer(self, fromView, toView):
        """ fromView and toView are QGraphicsWebViews
        @param fromView  datagraph.htmlvariableview.HtmlVariableView, starting point of the Pointer
        @param toView    datagraph.htmlvariableview.HtmlVariableView, end point of the Pointer
        """
        self._view.addItem(Pointer(None, fromView, toView, self.distributedObjects))

    def removePointer(self, pointer):
        """ removes the given pointer from the DataGraphView and the PointerList
        @param pointer    datagraph.pointer.Pointer, pointer to remove
        """
        self._view.removeItem(pointer)

    def clearDataGraph(self):
        """ clears the DataGraphView and the VariableList <br>
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        self.variableList.clear()
        self._view.clear()
