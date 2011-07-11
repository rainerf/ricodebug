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

from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from variablemodel import VariableModel, TreeItem
from localsmodel import LocalsModel
from localsview import LocalsView
from varwrapperfactory import VarWrapperFactory
from variables.variablelist import VariableList
from variables.variablewrapper import VariableWrapper

#####################################################################################
## WRAPPER CLASSES
#####################################################################################

class LocalsPtrVarWrapper(VariableWrapper, TreeItem):
    def __init__(self, variable):
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True
        
    def getChildren(self, factory):
        if (self.getChildCount() == 0):
            variable = self.variable.dereference()
            if variable != None:
                children = variable._getChildItems();
                if (len(children) == 0):
                    vwChild = variable.makeWrapper(factory)
                    vwChild.parent = self
                    self.addChild(vwChild)
                else:
                    for child in children:
                        vwChild = child.makeWrapper(factory)
                        vwChild.parent = self                   
                        self.addChild(vwChild)
        return self.childItems
    
class LocalsStructVarWrapper(VariableWrapper, TreeItem):
    def __init__(self, variable):
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True        

    def getChildren(self, factory):
        if (self.childItems.__len__() == 0):
            for child in self.variable.getChildren():
                vwChild = child.makeWrapper(factory)
                vwChild.parent = self
                self.addChild(vwChild)
                           
        return self.childItems;
    
class LocalsStdVarWrapper(VariableWrapper, TreeItem):
    def __init__(self, variable):
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True
        
#####################################################################################
## FACTORY
#####################################################################################
class LocalsVWFactory(VarWrapperFactory):
    def __init__(self):
        VarWrapperFactory.__init__(self)
        
    def makeStdVarWrapper(self, var):
        return LocalsStdVarWrapper(var)
    
    def makePtrVarWrapper(self, var):
        return LocalsPtrVarWrapper(var)
    
    def makeStructVarWrapper(self, var):
        return LocalsStructVarWrapper(var)


class LocalsController(QObject):
    
    def __init__(self, distributed_objects):
        QObject.__init__(self)
        self.distributedObjects = distributed_objects
        
        self.vwFactory = LocalsVWFactory()
        
        self.localsModel = LocalsModel(self, self.distributedObjects)
        self.localsView = LocalsView()
        
        self.localsView.treeView.setModel(self.localsModel)
        self.localsVariableList = VariableList(self.vwFactory, self.distributedObjects)
        
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('inferiorStoppedNormally(PyQt_PyObject)'), self.getLocals)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('cleanupModels()'), self.clearLocals)
        
    def insertDockWidgets(self):
        self.localsDock = QDockWidget("Locals")
        self.localsDock.setObjectName("LocalsView")
        self.localsDock.setWidget(self.localsView)
        self.distributedObjects.signal_proxy.addDockWidget(Qt.BottomDockWidgetArea, self.localsDock, True)
        
    def clearLocals(self):
        # clear lists
        del self.localsVariableList.list[:]
        self.localsModel.clear()

        
    def getLocals(self):
        self.clearLocals()
        self.localsVariableList.addLocals()
        
        for vw in self.localsVariableList.list:
            vw.setParent(self.localsModel.root)
            # add variable to root children
            self.localsModel.root.addChild(vw)
            self.localsModel.addVar(vw)
