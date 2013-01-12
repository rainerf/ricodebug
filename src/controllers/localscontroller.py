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

from models.localsmodel import LocalsModel
from .treeitemcontroller import TreeItemController
from helpers.icons import Icons


class LocalsController(TreeItemController):
    def __init__(self, distributedObjects, view):
        TreeItemController.__init__(self, distributedObjects, "Locals", view, LocalsModel, True, Icons.locals)

        self.returnWrapper = None

        self.distributedObjects.signalProxy.inferiorStoppedNormally.connect(self.getLocals)
        self.distributedObjects.stackController.stackFrameSelected.connect(self.getLocals)

    def getLocals(self, rec):
        # if we previously showed some return value, remove it; getLocals will
        # be called after the user steps/conts/... the program, most probably
        # making it out of date
        if self.returnWrapper:
            self.variableList.removeVar(self.returnWrapper)
            self.returnWrapper = None

        # now, check if there was a return value of a function in this record;
        # if so, add it to the locals and give it a meaningful name
        for r in rec.results:
            if r.dest == "gdb-result-var":
                self.returnWrapper = self.variableList.addVarByName(r.src)
                self.returnWrapper._v.exp = "Return value"

        # we're doing some sorting magic here: tuples will be sorted by the
        # second element if the first is equal; also, False < True, therefore
        # invert the boolean arg to have arguments first
        locals_ = sorted(self.distributedObjects.gdb_connector.getLocals(), key=lambda x: (not x.arg, x.name))
        current = [x for x in self.variableList.list]

        for l in locals_:
            for c in current:
                if l.name == c.exp:
                    current.remove(c)
                    break
            else:
                vw = self.variableList.addVarByName(l.name)
                vw._v.arg = l.arg
                self.add(vw)

        # we removed everything from current that's still there; therefore,
        # everything that's left here is out of scope
        for old in current:
            self.variableList.removeVar(old)
