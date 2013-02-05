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

from PyQt4.QtCore import QObject, pyqtSignal
from . import filters


class VariableWrapper(QObject):
    """ Parent of all Variable-Wrapper-Classes """

    dataChanged = pyqtSignal()

    def __init__(self, variable):
        """ Constructor
        @param  variable    Variable to wrap
        """
        QObject.__init__(self)
        self._v = variable
        self._v.changed.connect(self.varChanged)

        self.filter = filters.Empty

    def varChanged(self):
        self.dataChanged.emit()

    def __getitem__(self, item):
        return self._v[item]

    def __getattr__(self, name):
        # delegate the accesses to the wrapped variable
        if name in ["exp",
                    "type",
                    "inScope",
                    "access",
                    "uniqueName",
                    "assignValue",
                    "childs"]:
            return getattr(self._v, name)
        else:
            raise AttributeError("%s instance has no attribute '%s'" %
                                 (self.__class__.__name__, name))

    def die(self):
        self._v.changed.disconnect()
        self._v.die()

    value = property(lambda self: self.filter.toDisplay(self.unfilteredValue))
    unfilteredValue = property(lambda self: self._v.value)
