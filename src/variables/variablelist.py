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


class VariableList:
    def __init__(self, factory, do):
        """ Constructor
        @param factory    factory for constructing the variables added to this list
        @param do         distributedobjects.DistributedObjects, the DistributedObjects-Instance """
        self.varPool = do.variablePool
        self.factory = factory
        self._vars = []

    def addVarByName(self, varName):
        var = self.varPool.getVar(self.factory, str(varName))
        self._vars.append(var)
        return var

    def removeVar(self, var):
        self._vars.remove(var)
        var.die()

    def removeIdx(self, idx):
        """ removes the variable at index idx """
        var = self._vars.pop(idx)
        var.die()

    def clear(self):
        """ Clears the whole VariableList. """
        for var in self._vars:
            var.die()
        self._vars = []

    def __len__(self):
        return len(self._vars)

    def __getitem__(self, i):
        return self._vars[i]

    def items(self):
        return self._vars
