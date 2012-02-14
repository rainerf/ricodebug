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
from helpers.signalproxy import SignalProxy
from debugcontroller import DebugController
from variables.varwrapperfactory import VarWrapperFactory
from variables.stdvariablewrapper import StdVariableWrapper
from variables.ptrvariablewrapper import PtrVariableWrapper
from variables.structvariablewrapper import StructVariableWrapper
from variables.variablelist import VariableList


class WatchVWFactory(VarWrapperFactory):
    def __init__(self):
        VarWrapperFactory.__init__(self)

    def makeStdVarWrapper(self, var):
        return StdVariableWrapper(var)

    def makePtrVarWrapper(self, var):
        return PtrVariableWrapper(var)

    def makeStructVarWrapper(self, var):
        return StructVariableWrapper(var)


class VariableController(QObject):
    _instance = None

    @classmethod
    def CreateInstance(cls, watchview):
        if not cls._instance:
            cls._instance = cls(watchview)

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            raise "VariableController has no Instance!"
        return cls._instance

    def __init__(self, watchview):
        QObject.__init__(self)

        #signalproxy
        self.signalProxy = SignalProxy.getInstance()
        QObject.connect(self.signalProxy, SIGNAL('AddWatch(QString)'), self.addWatch)

        # views
        self.watchview = watchview

        # controllers
        self.debugController = DebugController.getInstance()

        # factory
        self.vwFactory = WatchVWFactory()
        self.variableList = VariableList(self.vwFactory)

        # models
        self.variableModel = self.debugController.variableModel

    def addWatch(self, watch):
        var = self.variableList.addVar(watch)
        QObject.connect(var, SIGNAL('changed()'), self.varChanged)
#        for item in self.variableList:
#            print item.getExp() + " " + item.getValue()
#
#    def varChanged(self):
#        print "variable changed"

    def removeSelected(self, row, parent):
        self.variableModel.removeRow(row, parent)
