from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from variablemodel import TreeItem
from varwrapperfactory import VarWrapperFactory
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
        self.visible = True
        
    def getChildren(self, factory):
        """ Get children for TreePtrVarWrapper <br>
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
    
class TreeStructVarWrapper(VariableWrapper, TreeItem):
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
        """ Get children for TreePtrVarWrapper <br>
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
        self.visible = True


#####################################################################################
## FACTORY
#####################################################################################
class TreeVWFactory(VarWrapperFactory):
    def __init__(self):
        """ Constructor <br>
            create new TreeVWFactory
        """
        VarWrapperFactory.__init__(self)
        
    def makeStdVarWrapper(self, var):
        """ create StdVarWrapper
        """
        return TreeStdVarWrapper(var)
    
    def makePtrVarWrapper(self, var):
        """ create PtrVarWrapper
        """
        return TreePtrVarWrapper(var)
    
    def makeStructVarWrapper(self, var):
        """ create StructVarWrapper
        """
        return TreeStructVarWrapper(var)
    
    def makeArrayVarWrapper(self, var):
        """ create PendingVarWrapper
        """
        return TreeArrayVarWrapper(var)


#####################################################################################
## CONTROLLER
#####################################################################################
class TreeItemController(QObject):
    """ the Controller for the TreeView """
    def __init__(self, distributedObjects, name, view, model):
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
        self.view = view(self)
        
        self.view.setModel(self.model)
        self.variableList = VariableList(self.vwFactory, self.distributedObjects)
        
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('cleanupModels()'), self.clear)
        
    def clear(self):
        """ clears the TreeView and the VariableList <br>
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        # clear lists
        del self.variableList.list[:]
        self.model.clear()
        
    def insertDockWidgets(self):
        """ adds the Tree-DockWidget to the GUI <br>
            this function is connected to the signal SignalProxy::insertDockWidgets() """
        dock = QDockWidget(self.name)
        dock.setObjectName(self.name + "View")
        dock.setWidget(self.view)
        self.distributedObjects.signal_proxy.addDockWidget(Qt.BottomDockWidgetArea, dock, True)

    def add(self, vw):
        vw.setParent(self.model.root)
        
        # add children
        self.model.root.addChild(vw)
        self.model.addVar(vw)
