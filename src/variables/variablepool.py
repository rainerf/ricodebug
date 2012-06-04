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
from helpers.gdboutput import GdbOutput
from stdvariable import StdVariable
from ptrvariable import PtrVariable
from structvariable import StructVariable
from arrayvariable import ArrayVariable
import logging
import re
from helpers.excep import VariableNotFoundException


class VariablePool(QObject):
    """ Variablepool holding all variables created once from a view """

    def __init__(self, distributedObjects):
        """ Constructor
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QObject.__init__(self)

        self.distributedObjects = distributedObjects
        self.debugcontroller = distributedObjects.debugController
        self.connector = distributedObjects.gdb_connector
        #self.list = {}
        self.variables = {}

        # signalproxy
        self.signalProxy = distributedObjects.signalProxy
        self.distributedObjects.signalProxy.tracepointOccurred.connect(self.justUpdateValues)
        self.distributedObjects.signalProxy.inferiorStoppedNormally.connect(self.updateVars)
        self.distributedObjects.signalProxy.cleanupModels.connect(self.clearVars)

    def clearVars(self):
        """ delete all variables stored in pool
            this function is connected to the signal SignalProxy::cleanupModels()
        """

        self.variables = {}

    def justUpdateValues(self):
        """ just update variables for tracepoints, dont signal changes to connected views
        this function is connected to the signal SignalProxy::tracepointOccured()
        """
        self.__updateVars(True)
        # signal TracepointController about finished update
        self.distributedObjects.signalProxy.emitDataForTracepointsReady()

    def updateVars(self):
        """ update variables if inferiorStoppedNormally
        this function is connected to the signal SignalProxy::inferiorStoppedNormally(PyQt_PyObject)
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
            var = self.variables[changed.name]
            var.inscope = (changed.in_scope == "true")
            if hasattr(changed, "value"):
                var.value = changed.value
            if not isTracePoint:
                var.emitChanged()

        self.signalProxy.emitVariableUpdateCompleted()

    def addLocals(self):
        """ get locals from gdb and add to pool if variable is not existing
        """
        ret = []
        res = self.connector.getLocals()

        for x in reversed(res):
            var = self.getVar(x.name)
            ret.append(var)
        return ret

    def getVar(self, exp):
        """ return variable from pool if already existing <br>
            if variable is not existing in pool, create new GDB variable and add to pool
        @param exp       string, expression from variable to return
        """
        # get variable from gdb (fixed)
        gdbVar = self.connector.var_create("- * " + str(exp))

        if gdbVar.class_ == GdbOutput.ERROR:
            logging.error("Variable '%s' not found!", exp)
            raise VariableNotFoundException()

        # create variable
        varReturn = self.__createVariable(gdbVar, None, exp, None)

        self.variables[varReturn.gdbname] = varReturn

        logging.debug("Returning internal variable %s for expression %s",
                varReturn.gdbname, exp)

        return varReturn

    def getChildren(self, name, childList, access, parentName, childformat):
        """
        Appends the children of the variable with name to childList (and to internal list).
        These children are Variables.
        @param name         string, name of the variable to get children from
        @param childList    Variable[], list of children for variable
        @param access       string, variable is private, protected or public (read from gdb)
        @param parentName   unique name for parent item of children (e.g mystruct.value)
        @param childformat  string, template for forming a child's expression
        """
        gdbChildren = self.connector.var_list_children(name)
        if hasattr(gdbChildren, "children"):
            for child in gdbChildren.children:
                assert (child.dest == "child")

                if not hasattr(child.src, "type"):  # public, private, protected
                    access = child.src.exp
                    self.getChildren(child.src.name, childList, access, parentName, "%(parent)s.%(child)s")
                elif child.src.exp == child.src.type:   # base classes
                    self.getChildren(child.src.name, childList, access, parentName, "%(parent)s.%(child)s")
                else:
                    var = self.__createVariable(child.src, parentName, None, access, childformat)
                    self.variables[var.gdbname] = var
                    childList.append(var)

    def assignValue(self, gdbName, value):
        """
        Assigns the value from the variable to the gdbvariable
        Only used when setValue method is called
        @param gdbName     string, GDB name of value
        @param value       new value for variable
        """
        res = self.connector.var_assign(gdbName, str(value))
        if res.class_ == GdbOutput.ERROR:
            logging.error("Error when assigning variable: %s", res.raw)

        # update _all_ vars; other expressions in the variable pool might depend
        # on what we just changed!
        self.updateVars()

    def __createVariable(self, gdbVar, parentName=None, exp=None, access=None, childformat=None):
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
        type_ = None
        value = None
        inscope = None
        haschildren = None

        if hasattr(gdbVar, "exp"):
            exp = gdbVar.exp
        gdbName = gdbVar.name
        if parentName == None:
            uniqueName = exp
        else:
            uniqueName = childformat % {"parent": parentName, "child": exp}
        type_ = gdbVar.type
        value = gdbVar.value
        inscope = True
        haschildren = (int(gdbVar.numchild) > 0)
        access = access

        # We use some heuristics to find out whether a type is a pointer, an
        # array, or a structure:
        # * Pointers will have addresses as their values, ie. their value will
        # start with "0x"
        # * Arrays will have their size as their value as reported by gdb.
        # Therefore, if the value looks like a size, treat it as an array.
        # * Everything else with children is a structure.
        # * Again, everything else is a normal variable.
        if gdbVar.value.startswith('0x') and int(gdbVar.numchild) >= 1:
            logging.debug("Creating a pointer variable for '%s'", exp)
            varReturn = PtrVariable(self, exp, gdbName, uniqueName, type_, value, inscope, haschildren, access)
        elif re.match("\[\d+\]", gdbVar.value) and int(gdbVar.numchild) >= 1:
            logging.debug("Creating a array variable for '%s'", exp)
            varReturn = ArrayVariable(self, exp, gdbName, uniqueName, type_, value, inscope, haschildren, access)
        elif haschildren:
            logging.debug("Creating a struct variable for '%s'", exp)
            varReturn = StructVariable(self, exp, gdbName, uniqueName, type_, value, inscope, haschildren, access)
        else:
            logging.debug("Creating a normal variable for '%s'", exp)
            varReturn = StdVariable(self, exp, gdbName, uniqueName, type_, value, inscope, haschildren, access)

        return varReturn

    #def dump(self):
    #    for exp, var in self.list.items():
    #        print exp, var
