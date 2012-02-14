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
from stdvariablewrapper import StdVariableWrapper
from ptrvariablewrapper import PtrVariableWrapper
from structvariablewrapper import StructVariableWrapper
from arrayvariablewrapper import ArrayVariableWrapper
from pendingvariablewrapper import PendingVariableWrapper


class VarWrapperFactory(QObject):
    """ Factory-Class for VariableWrappers. <br>
        Creates VariableWrappers.
    """

    def __init__(self):
        """ Constructor """
        QObject.__init__(self)

    def makeStdVarWrapper(self, var):
        """ creates a StdVariableWrapper for the given Variable
        @param var     the Variable to create a StdVariableWrapper for
        @return        variables.stdvariablewrapper.StdVariableWrapper, StdVariableWrapper for the given Variable
        """
        return StdVariableWrapper(var)

    def makePtrVarWrapper(self, var):
        """ creates a PtrVariableWrapper for the given Variable
        @param var     the Variable to create a PtrVariableWrapper for
        @return        variables.ptrvariablewrapper.PtrVariableWrapper, PtrVariableWrapper for the given Variable
        """
        return PtrVariableWrapper(var)

    def makeStructVarWrapper(self, var):
        """ creates a StructVariableWrapper for the given Variable
        @param var     the Variable to create a StructVariableWrapper for
        @return        variables.structvariablewrapper.StructVariableWrapper, StructVariableWrapper for the given Variable
        """
        return StructVariableWrapper(var)

    def makeArrayVarWrapper(self, var):
        """ creates an ArrayVariableWrapper for the given Variable
        @param var     the Variable to create a ArrayVariableWrapper for
        @return        variables.arrayvariablewrapper.ArrayVariableWrapper, ArrayVariableWrapper for the given Variable
        """
        return ArrayVariableWrapper(var)

    def makePendingVarWrapper(self, var):
        """ creates a PendingVariableWrapper for the given Variable
        @param var     the Variable to create a PendingVariableWrapper for
        @return        variables.pendingvariablewrapper.PendingVariableWrapper, PendingVariableWrapper for the given Variable
        """
        return PendingVariableWrapper(var)
