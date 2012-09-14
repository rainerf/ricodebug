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
from .stdvariablewrapper import StdVariableWrapper
from .ptrvariablewrapper import PtrVariableWrapper
from .structvariablewrapper import StructVariableWrapper
from .arrayvariablewrapper import ArrayVariableWrapper


class VarWrapperFactory(QObject):
    def makeWrapper(self, var):
        func = "make%sWrapper" % var.__class__.__name__
        return getattr(self, func)(var)

    def makeStdVariableWrapper(self, var):
        return StdVariableWrapper(var)

    def makePtrVariableWrapper(self, var):
        return PtrVariableWrapper(var)

    def makeStructVariableWrapper(self, var):
        return StructVariableWrapper(var)

    def makeArrayVariableWrapper(self, var):
        return ArrayVariableWrapper(var)
