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
from models.variablemodel import TreeItem
from variables.varwrapperfactory import VarWrapperFactory
from variables.variablelist import VariableList
from variables.variablewrapper import VariableWrapper

#####################################################################################
## WRAPPER CLASSES
#####################################################################################


class TreePtrVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Pointer-Variables """

    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False

    def getChildren(self, factory):
        """ Get children for TreePtrVarWrapper <br>
            dereference PtrVariable and get Children from VariableList
        @param factory   derived from VarWrapperFactory, factory to look in VariableList for children
        """
        if (self.getChildCount() == 0):
            variable = self._v.dereference()
            if variable is not None:
                if not variable.hasChildren:
                    vwChild = variable.makeWrapper(factory)
                    vwChild.parent = self
                    vwChild.dataChanged.connect(vwChild.hasChanged)
                    self.addChild(vwChild)
                else:
                    for child in variable.childs:
                        vwChild = child.makeWrapper(factory)
                        vwChild.parent = self
                        vwChild.dataChanged.connect(vwChild.hasChanged)
                        self.addChild(vwChild)
        return self.childItems

    def hasChanged(self):
        """ overrides method from TreeItem <br>
            remove all children from pointer if value has changed
            this function is connected to the signal SignalProxy::changed()
        """
        self.removeChildren()
        self.setChanged(True)


class TreeStructVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Struct-Variables """

    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False

    def getChildren(self, factory):
        """ Get children for TreePtrVarWrapper <br>
            Get Children from VariableList for StructVariable
        @param factory   derived from VarWrapperFactory, factory to look in VariableList for children
        """
        if (len(self.childItems) == 0) or (self._v.numChild != len(self.childItems)):
            self.removeChildren()
            for child in self._v.childs:
                vwChild = child.makeWrapper(factory)
                vwChild.parent = self
                vwChild.dataChanged.connect(vwChild.hasChanged)                    
                self.addChild(vwChild)
                self._v.numChild = len(self.childItems)

        return self.childItems


class TreeArrayVarWrapper(TreeStructVarWrapper):
    pass


class TreeStdVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Standard-Variables """

    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False


#####################################################################################
## FACTORY
#####################################################################################
class TreeVWFactory(VarWrapperFactory):
    def __init__(self):
        """ Constructor <br>
            create new TreeVWFactory
        """
        VarWrapperFactory.__init__(self)

    def makeStdVariableWrapper(self, var):
        return TreeStdVarWrapper(var)

    def makePtrVariableWrapper(self, var):
        return TreePtrVarWrapper(var)

    def makeStructVariableWrapper(self, var):
        return TreeStructVarWrapper(var)

    def makeArrayVariableWrapper(self, var):
        return TreeArrayVarWrapper(var)


#####################################################################################
## CONTROLLER
#####################################################################################
class TreeItemController(QObject):
    """ the Controller for the TreeView """
    def __init__(self, distributedObjects, name, view, model, addDockWidget):
        """ Constructor <br>
            Create a TreeView, a TreeVWFactory and a VariableList <br>
            Listens to the following Signals: SignalProxy::AddTree(QString), SignalProxy::insertDockWidgets() and SignalProxy::cleanupModels()
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QObject.__init__(self)
        self.distributedObjects = distributedObjects

        self.name = name
        self.vwFactory = TreeVWFactory()

        self.model = model(self, self.distributedObjects)
        self.view = view
        self.view.controller = self
        self.view.setModel(self.model)
        self.variableList = VariableList(self.vwFactory, self.distributedObjects)

        self.distributedObjects.signalProxy.cleanupModels.connect(self.clear)

        if addDockWidget:
            self.distributedObjects.mainwindow.insertDockWidget(self.view, name, Qt.BottomDockWidgetArea, True)

    def clear(self):
        """ clears the TreeView and the VariableList <br>
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        # clear lists
        self.variableList.clear()
        self.model.clear()

    def add(self, vw):
        vw.setParent(self.model.root)

        # add children
        self.model.root.addChild(vw)
        self.model.addVar(vw)
