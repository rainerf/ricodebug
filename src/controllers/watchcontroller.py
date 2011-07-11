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

from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from variablemodel import VariableModel
from watchview import WatchView
from variablemodel import TreeItem
from varwrapperfactory import VarWrapperFactory
from variables.variablelist import VariableList
from variables.variablewrapper import VariableWrapper
        
#####################################################################################
## WRAPPER CLASSES
#####################################################################################

class WatchPtrVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Pointer-Variables """
    
    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap 
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True
        
    def getChildren(self, factory):
        """ Get children for WatchPtrVarWrapper <br>
            dereference PtrVariable and get Children from VariableList
        @param factory   derived from VarWrapperFactory, factory to look in VariableList for children
        """
        if (self.getChildCount() == 0):
            variable = self.variable.dereference()
            if variable != None:
                children = variable._getChildItems();
                if (len(children) == 0):
                    vwChild = variable.makeWrapper(factory)
                    vwChild.parent = self
                    QObject.connect(vwChild, SIGNAL('changed()'), vwChild.hasChanged)
                    self.addChild(vwChild)
                else:
                    for child in children:
                        vwChild = child.makeWrapper(factory)
                        vwChild.parent = self         
                        QObject.connect(vwChild, SIGNAL('changed()'), vwChild.hasChanged)               
                        self.addChild(vwChild)
        return self.childItems
    
    def hasChanged(self):
        """ overrides method from TreeItem <br>
            remove all children from pointer if value has changed
            this function is connected to the signal SignalProxy::changed()
        """
        self.removeChildren()
        self.setChanged(True)        
    
class WatchStructVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Struct-Variables """
    
    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap 
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True        

    def getChildren(self, factory):        
        """ Get children for WatchPtrVarWrapper <br>
            Get Children from VariableList for StructVariable
        @param factory   derived from VarWrapperFactory, factory to look in VariableList for children
        """
        if (self.childItems.__len__() == 0):
            for child in self.variable.getChildren():
                vwChild = child.makeWrapper(factory)
                vwChild.parent = self
                QObject.connect(vwChild, SIGNAL('changed()'), vwChild.hasChanged)
                self.addChild(vwChild)
                           
        return self.childItems;
    
class WatchStdVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Standard-Variables """
    
    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap 
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True
        
class WatchPendingVarWrapper(VariableWrapper, TreeItem):
    """ VariableWrapper for Pending-Variables """
    def __init__(self, variable):
        """ Constructor
        @param variable   Variable, varible to wrap 
        """
        VariableWrapper.__init__(self, variable)
        TreeItem.__init__(self)
        self.valueChanged = False
        self.visible = True
        
#####################################################################################
## FACTORY
#####################################################################################
class WatchVWFactory(VarWrapperFactory):
    def __init__(self):
        """ Constructor <br>
            create new WatchVWFactory
        """
        VarWrapperFactory.__init__(self)
        
    def makeStdVarWrapper(self, var):
        """ create StdVarWrapper
        """
        return WatchStdVarWrapper(var)
    
    def makePtrVarWrapper(self, var):
        """ create PtrVarWrapper
        """
        return WatchPtrVarWrapper(var)
    
    def makeStructVarWrapper(self, var):
        """ create StructVarWrapper
        """
        return WatchStructVarWrapper(var)
    
    def makePendingVarWrapper(self, var):
        """ create PendingVarWrapper
        """
        return WatchPendingVarWrapper(var)

#####################################################################################
## CONTROLLER
#####################################################################################
class WatchController(QObject):
    """ the Controller for the WatchView """
    
    def __init__(self, distributedObjects):
        """ Constructor <br>
            Create a WatchView, a WatchVWFactory and a VariableList <br>
            Listens to the following Signals: SignalProxy::AddWatch(QString), SignalProxy::insertDockWidgets() and SignalProxy::cleanupModels()
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QObject.__init__(self)
        self.distributedObjects = distributedObjects
        #self.root = RootVarWrapper()
        
        self.vwFactory = WatchVWFactory()
        
        self.variableModel = VariableModel(self, self.distributedObjects)
        self.watchView = WatchView(self)
        
        self.watchView.setModel(self.variableModel)
        self.watchVariableList = VariableList(self.vwFactory, self.distributedObjects)
        
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('AddWatch(QString)'), self.addWatch)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('cleanupModels()'), self.clearVars)
        
    def clearVars(self):
        """ clears the WatchView and the VariableList <br>
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        # clear lists
        del self.watchVariableList.list[:]
        self.variableModel.clear()     
        
    def insertDockWidgets(self):
        """ adds the Watch-DockWidget to the GUI <br>
            this function is connected to the signal SignalProxy::insertDockWidgets() """

        self.watchDock = QDockWidget("Watch")
        self.watchDock.setObjectName("WatchView")
        self.watchDock.setWidget(self.watchView)
        self.distributedObjects.signal_proxy.addDockWidget(Qt.BottomDockWidgetArea, self.watchDock, True)
        
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
        vw = self.watchVariableList.addVarByName(watch)
        # connect changed and replace signal from wrapper
        QObject.connect(vw, SIGNAL('changed()'), vw.hasChanged)  
        QObject.connect(vw, SIGNAL('replace(PyQt_PyObject, PyQt_PyObject)'), self.replaceVariable)  
        
        # set parent for root variable
        vw.setParent(self.variableModel.root)
        
        # add variable to root children
        self.variableModel.root.addChild(vw)
        self.variableModel.addVar(vw)
        
    def replaceVariable(self, pendingVar, newVar):
        """ replaces a variable in the variablelist
        @param pendingVar    variables.variablewrapper.VariableWrapper, VariableWrapper to replace in the list
        @param newVar        variables.Variable, new Variable which replaces existing VariableWrapper in List
        """
        vwOld = self.watchVariableList.getVariableWrapper(pendingVar)
        
        vwNew = self.watchVariableList.replaceVar(pendingVar, newVar)
        QObject.connect(vwNew, SIGNAL('changed()'), vwNew.hasChanged)  
        QObject.connect(vwNew, SIGNAL('replace(PyQt_PyObject, PyQt_PyObject)'), self.replaceVariable)  
        
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
            xmlHandler.createNode("Watch", watchParent, { 'exp': var.getExp()})
             
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
                
                
    
