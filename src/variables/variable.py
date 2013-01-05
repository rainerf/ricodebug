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


MIME_TYPE = "application/x-variableexpresssion"


class Variable(QObject):
    """ Class holding a Variable. <br>
        This is the Parent of all Variable-Classes and the Core of all VariableWrappers.
        It holds the most basic Elements of a Variable-Object, that are useful for all (or at least the most) purposes.
    """
    childFormat = None

    changed = pyqtSignal(str)

    def __init__(self, variablepool, exp, gdbName,
            uniqueName, type_, value, inScope,
            hasChildren, access):
        QObject.__init__(self)
        self.exp = exp
        self.type = type_
        self.inScope = inScope
        self.access = access
        self.uniqueName = uniqueName
        self.value = value
        self.hasChildren = hasChildren
        self.arg = False

        self._vp = variablepool
        self._gdbName = gdbName
        self._childs = []

    def _getChildrenFromGdb(self):
        """Load the children from GDB, if there are any."""
        if not self.hasChildren:
            raise AttributeError("No children available.")
        if not self._childFormat:
            raise AttributeError("No child format set.")

        if not self._childs:
            self._vp.getChildren(self._gdbName, self._childs, self.access, self.uniqueName, self._childFormat)

    def __getChilds(self):
        """Return the lazily loaded list of children."""
        self._getChildrenFromGdb()
        return self._childs
    childs = property(__getChilds)

    def getChildrenNames(self):
        """Return the names of all children."""
        return [i.exp for i in self.childs]

    def __getitem__(self, name):
        for i in self.childs:
            if i.exp == name:
                return i
        raise AttributeError("No child with name '%s'." % name)

    def assignValue(self, value):
        self._vp.assignValue(self._gdbName, value)

    def __str__(self):
        # we use self._childs instead of self.childs to make sure printing the
        # variable does not load its children if they are not already
        return "%s [%s]" % (self.__class__.__name__, " ".join([
                self._gdbName,
                self.type,
                str(self.value),
                "in scope" if self.inScope else "",
                "has children" if self.hasChildren else "",
                self.access if self.access else "",
                str(len(self._childs)) if self._childs else ""]))

    def emitChanged(self):
        self.changed.emit(self.value)

    def makeWrapper(self, factory):
        return factory.makeWrapper(self)

    def die(self):
        self._vp.removeVar(self)
