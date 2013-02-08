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
from variables import filters


MIME_TYPE = "application/x-variableexpresssion"


class Variable(QObject):
    """
    Class holding a Variable. This is the Parent of all Variable-Classes.
    """
    childFormat = None

    changed = pyqtSignal(str)

    def __init__(self, variablepool, factory, exp, gdbName,
            uniqueName, type_, value, inScope,
            numChildren, access):
        QObject.__init__(self)
        self.exp = exp
        self.type = type_
        self.inScope = inScope
        self.access = access
        self.uniqueName = uniqueName
        self._value = value
        self.numChildren = numChildren
        self.arg = False
        self.factory = factory

        self.__filter = filters.Empty

        self._vp = variablepool
        self._gdbName = gdbName
        self._childs = []

    hasChildren = property(lambda self: self.numChildren > 0)
    value = property(lambda self: self.__filter.toDisplay(self._value))

    def _loadChildrenFromGdb(self):
        """Load the children from GDB, if there are any."""
        if not self.hasChildren:
            raise AttributeError("No children available.")
        if not self._childFormat:
            raise AttributeError("No child format set.")

        if not self._childs:
            self._vp.getChildren(self.factory, self._gdbName, self._childs, self.access, self.uniqueName, self._childFormat)

    @property
    def childs(self):
        """Return the lazily loaded list of children."""
        if not self._childs:
            self._loadChildrenFromGdb()
        return self._childs

    def __getitem__(self, name):
        for i in self.childs:
            if i.exp == name:
                return i
        raise AttributeError("No child with name '%s'." % name)

    def assignValue(self, value):
        self._vp.assignValue(self._gdbName, self.__filter.fromDisplay(value))

    def __repr__(self):
        # we use self._childs instead of self.childs to make sure printing the
        # variable does not load its children if they are not already
        return "%s [%s]" % (self.__class__.__name__, " ".join([
                self.type,
                self.exp,
                str(self._value),
                self._gdbName,
                "children: %s" % str(self.numChildren),
                "in scope" if self.inScope else "",
                self.access if self.access else "",
                str(len(self._childs)) if self._childs else ""]))

    def emitChanged(self):
        self.changed.emit(self.value)

    def die(self):
        for c in self._childs:
            c.die()
        self._vp.removeVar(self)

    def setFilter(self, f):
        self.__filter = f
        self.emitChanged()
