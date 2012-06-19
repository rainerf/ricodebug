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

from controllers.treeitemcontroller import TreeItemController
from models.variablemodel import VariableModel
from helpers.excep import VariableNotFoundException


class ToolTipController(TreeItemController):
    def __init__(self, distributedObjects, view):
        TreeItemController.__init__(self, distributedObjects, "Tooltip", view, VariableModel, False)

    def __setVar(self, watch):
        self.clear()
        try:
            self.add(self.variableList.addVarByName(watch))
        except VariableNotFoundException:
            pass

    def showToolTip(self, exp, pos, parent):
        self.__setVar(exp)
        self.view.move(parent.mapToGlobal(pos))
        self.view.raise_()
        self.view.show(exp)

    def hideToolTip(self):
        self.view.hideLater()
