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

from PyQt4.QtCore import QObject, SIGNAL
from gdboutput import GdbOutput
from stdvariable import StdVariable
from ptrvariable import PtrVariable
from structvariable import StructVariable
from pendingvariable import PendingVariable

class VariablePool(QObject):
    """ Variablepool holding all variables created once from a view """
    
    def __init__(self, distributedObjects):
        """ Constructor
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QObject.__init__(self)
        
        self.distributedObjects = distributedObjects
        self.debugcontroller = distributedObjects.debug_controller
        self.connector = distributedObjects.gdb_connector
        self.list = {}
        self.pending = []
        
        # signalproxy
        self.signalProxy = distributedObjects.signal_proxy
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('tracepointOccurred()'), self.justUpdateValues)
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('inferiorHasStopped(PyQt_PyObject)'), self.updateVars)        
        QObject.connect(self.distributedObjects.signal_proxy, SIGNAL('cleanupModels()'), self.clearVars)
        
    def clearVars(self):
        """ delete all variables stored in pool 
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        
        self.list = {}
    
    def justUpdateValues(self):
        """ just update variables for tracepoints, dont signal changes to connected views
        this function is connected to the signal SignalProxy::tracepointOccured()
        """
        self.__updateVars(True)
        # signal TracepointController about finished update
        self.distributedObjects.signal_proxy.emitDataForTracepointsReady()
    
    def updateVars(self):
        """ update variables if inferiorHasStopped
        this function is connected to the signal SignalProxy::inferiorHasStopped(PyQt_PyObject)
        """
        self.__updateVars(False)
    
    def __updateVars(self, isTracePoint=None):
        """ get updates for variables from gdb
        @param isTracePoint   bool, if method is called from Tracepoint<br>
                              changed signal is not emitted 
        """
        
        res = self.connector.var_update("*")
        if not hasattr(res, "changelist"):
            return
        res = res.changelist
         
        # update the variable
        # dont use setter method to apply changes because this will cause update to gdb
        # just update value in pool
        for changed in res:
            for var in self.list.itervalues():
                if var.getGdbName() == changed.name:
                    if (var.inscope != (bool(changed.in_scope == "true"))):                                                
                        var.inscope = (bool(changed.in_scope == "true"))                                       
                    if (hasattr(changed, "value")):    
                        var.value = changed.value                           
                    if isTracePoint == False:
                        var.changed()
        
        # search for pending varialbes and replace them if
        # they are in scope
        tempList = self.list.copy()
        for var in tempList.itervalues():
            if var.getPending() == True:
                gdbVar = self.connector.var_create("- * " + var.getExp())
                if (gdbVar.class_ != GdbOutput.ERROR):
                    newVar = self.__createVariable(gdbVar, None, var.getExp(), None)
                    self.list[var.getUniqueName()] = newVar
                    var.replace(newVar)
                    
    def addLocals(self):
        """ get locals from gdb and add to pool if variable is not existing
        """
        ret = []
        res = self.connector.getLocals()
        
        for x in reversed(res):         
            var = self.getVar(x.name, True)
            ret.append(var)
        return ret        

    def getVar(self, exp, isLocal=False):
        """ return variable from pool if already existing <br>
            if variable is not existing in pool, create new GDB variable and add to pool
        @param exp       string, expression from variable to return
        @param isLocal   bool, replace pending variables from pool if variable is local variable
        """
        varReplace = None
        
        # variable existing in pool and in current scope
        if (self.list.has_key(exp) == True):            
            # if variable went out of scope but also exists in current scope
            # delete it and recreate on gdb
            if (self.list[exp].getInScope() == False and isLocal == True):
                varReplace = self.list[exp]                
                del self.list[exp] 
                  
            # return variable from pool if not pending      
            elif self.list[exp].getPending() == False:
                return self.list[exp]
            # replace pending variable
            else:
                varReplace = self.list[exp]
                del self.list[exp] 

        # get variable from gdb (fixed)
        gdbVar = self.connector.var_create("- * " + str(exp))            
        
        # successful result
        if (gdbVar.class_ == GdbOutput.ERROR):
            gdbVar = None
        
        # create variable
        varReturn = self.__createVariable(gdbVar, None, exp, None) 
        
        if varReplace != None:
            varReplace.replace(varReturn)
            
        self.list[varReturn.getUniqueName()] = varReturn
        
        return varReturn
    
    def getChildren(self, name, childList, access, parentName):
        """
        Appends the children of the variable with name to childList (and to internal list).
        These children are Variables.  
        @param name         string, name of the variable to get children from
        @param childList    Variable[], list of children for variable
        @param access       string, variable is private, protected or public (read from gdb)
        @param parentName   unique name for parent item of children (e.g mystruct.value)   
        """
        gdbChildren = self.connector.var_list_children(name)
        if (hasattr(gdbChildren, "children") == True):
            for child in gdbChildren.children:
                assert (child.dest == "child")
            
                if ((hasattr(child.src, "type") == False) or    # public, private, protected
                        child.src.exp == child.src.type):       # base classes
                    access = child.src.exp
                    #parentName = parentName + "." + access
                    self.getChildren(child.src.name, childList, access, parentName)
                # add variable to childList
                else:
                    # variable existing in pool and in current scope
                    uniqueName = str(parentName + "." + child.src.exp)
                    if (self.list.has_key(uniqueName) == True):     
                        var =  self.list[uniqueName]
                    else:
                        var = self.__createVariable(child.src, parentName, None, access)
                    self.list[var.getUniqueName()] = var
                    childList.append(var) 
                    
    def assignValue(self, gdbName, value):
        """
        Assigns the value from the variable to the gdbvariable
        Only used when setValue method is called
        @param gdbName     string, GDB name of value
        @param value       new value for variable
        """
        res = self.connector.var_assign(gdbName, str(value.toString()))
        if res.class_ == GdbOutput.ERROR:
            print "[VarModel] got error: " + res.raw
            raise
    
    def __createVariable(self, gdbVar, parentName=None, exp=None, access=None):          
        """ create Variable with value from gdb variable
        @param gdbVar        variable read from gdb
        @param parentName    string, name of the parent item
        @param exp           expression of the variable
        @param access        string, accessor of variable (private, protected, public)
        """
        # variable to create
        varReturn = None
        
        # initialize values
        gdbName = None
        uniqueName = None
        type = None
        value = None
        inscope = None
        haschildren = None
        
        # PendingVariable
        if gdbVar == None:
            uniqueName = exp
            inscope = False
            varReturn = PendingVariable(self, exp, gdbName, uniqueName, type, value, inscope, haschildren, access)            
        else:
            if hasattr(gdbVar, "exp"):
                exp = gdbVar.exp
            gdbName = gdbVar.name
            if parentName == None:
                uniqueName = exp
            else:
                uniqueName = "(" + parentName + ")." + exp
            type = gdbVar.type
            value = gdbVar.value
            inscope = True
            haschildren = (int(gdbVar.numchild) > 0)
            access = access
                
            # PtrVariable
            if type.find("*") >= 0:
                varReturn = PtrVariable(self, exp, gdbName, uniqueName, type, value, inscope, haschildren, access)
            # StructVariable
            elif haschildren == True:
                varReturn = StructVariable(self, exp, gdbName, uniqueName, type, value, inscope, haschildren, access)
            #StdVariable      
            else:
                varReturn = StdVariable(self, exp, gdbName, uniqueName, type, value, inscope, haschildren, access)
                
        return varReturn

