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

from PyQt4.QtCore import Qt
from .breakpointmodel import Breakpoint
from variables.variablelist import VariableList
from helpers.tools import cpp2py
from models.breakpointmodel import BreakpointModel
from helpers.icons import Icons
from variables.plainvariablefactory import PlainVariableFactory


class ValueList:
    """This class provides a name and a list of values
    """
    def __init__(self, name, type_):
        self.name = name
        self.values = []
        self.type = type_

    def addValue(self, type_, val):
        if self.type != type_:
            self.type = type_
        if type_ == "int":
            self.values.append(int(val))
        elif type_ == "bool":
            self.values.append(cpp2py(val))
        elif type_ == "float" or self.type == "double":
            self.values.append(float(val))

    def clear(self):
        self.values = []


class Tracepoint(Breakpoint):
    """This class is used as a tracepoint in tracepointmodel.
    Basically Tracpoints are Breakpoint but they are extended
    with tracedVariables (list of Variable-Value-Pairs).
    Every Tracepoint contains some variables that are traced.
    Tracepoints are breakpoints and stop program then get
    information of asked variables and then continue program
    """

    def __init__(self, breakpoint, connector, do, nr):
        Breakpoint.__init__(self, breakpoint, connector)
        self.name = "TP #%s" % nr
        self.variableList = VariableList(PlainVariableFactory, do)
        self.wave = []
        self.autoContinue = True

        self.tooltip = "Tracepoint"

    icon = property(lambda self: Icons.tp if self.enabled else Icons.bp_dis)
    tracedVariables = property(lambda self: [v.exp for v in self.variableList])

    def addVar(self, variableToTrace):
        """ add a var to trace its value
        @param variableToTrace: variable name of the variable that should be traced"""
        vw = self.variableList.addVarByName(variableToTrace)
        newValueList = ValueList(variableToTrace, vw.type)
        self.wave.append(newValueList)

        # FIXME: emit dataChanged to make sure the views are updated

    def recordData(self):
        """tracepoint occurred: get values of all traced variables then continue debugging """
        for varList in self.wave:
            for v in self.variableList.items():
                if v.uniqueName == varList.name:
                    varList.addValue(v.type, v.value)


class TracepointModel(BreakpointModel):
    def __init__(self, do, parent=None):
        BreakpointModel.__init__(self, do, parent)
        self.do = do

    def _newBreakpoint(self, bkpt, connector, **kwargs):
        return Tracepoint(bkpt, connector, self.do, self.__getTpNumber(0))

    def __getTpNumber(self, nr):
        '''@return int - lowest, not used tp number'''
        for tp in self.breakpoints:
            if tp.name.endswith(str(nr)):
                return self.__getTpNumber(nr + 1)
        return nr

    def clearTracepointData(self):
        ''' Clear traced data of breakpoints'''
        for tp in self.breakpoints:
            for val in tp.wave:
                val.clear()

    def handleTracepoint(self, bpInfo):
        """handles occured tracepoint
        @param bpInfo: bpInfo.fullname = filename  bpInfo.line = line of tracepoint
        """
        for tp in self.breakpoints:
            if tp.fullname == bpInfo.fullname and int(tp.line) == int(bpInfo.line):
                tp.tracePointOccured()

    def columnCount(self, parent):
        return BreakpointModel.columnCount(self, parent) + 1

    def data(self, index, role):
        if index.column() < BreakpointModel.columnCount(self, None):
            return BreakpointModel.data(self, index, role)

        ret = None

        tp = self.breakpoints[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == self.columnCount(None) - 1:
                ret = ", ".join(tp.tracedVariables)

        return ret

    def headerData(self, section, orientation, role):
        if section < BreakpointModel.columnCount(self, None):
            return BreakpointModel.headerData(self, section, orientation, role)

        ret = None

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == self.columnCount(None) - 1:
                    ret = "Traced Variables"

        return ret

    def flags(self, index):
        if index.column() < BreakpointModel.columnCount(self, None):
            return BreakpointModel.flags(self, index)

        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return f

    def selectionMade(self, index):
        """ called if row in TracepointView is clicked, start to update wave in tracepointWaveView
        @param index: index of row that was clicked
        """
        tp = self.breakpoints[index.row()]
        self.do.tracepointwaveController.updateTracepointWaveView(tp.wave)
