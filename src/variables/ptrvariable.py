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

from variables.variable import Variable


class PtrVariable(Variable):
    _childFormat = "(*%(parent)s)"

    def _pointerValid(self):
        return self.value != "0x0"

    def dereference(self):
        """ Dereferences the Variable, if possible.
        @return    dereferenced Variable if the Variable can be dereferenced
        """
        # avoid null-pointer dereference
        if self._pointerValid():
            return self._vp.getVar(self.factory, self._childFormat % {"parent": self.uniqueName})
        else:
            return None

    def _loadChildrenFromGdb(self):
        if len(self._childs) == 0 and self._pointerValid():
            self._childs = [self._vp.getVar(self.factory, self._childFormat % {"parent": self.uniqueName})]

    def __getitem__(self, name):
        if name != "*":
            raise ValueError("PtrVariable needs to be dereferenced (index [\"*\"])")
        assert len(self.childs) == 1
        return self.childs[0]
