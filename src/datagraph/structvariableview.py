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

from .datagraphvariables import ComplexDataGraphVariableBase, ComplexTemplateHandler
from variables.structvariable import StructVariable


class StructVariableTemplateHandler(ComplexTemplateHandler):
    def __init__(self, var):
        ComplexTemplateHandler.__init__(self, var, 'structvariableview.mako')


class DataGraphStructVariable(StructVariable, ComplexDataGraphVariableBase):
    def __init__(self, *args):
        StructVariable.__init__(self, *args)
        ComplexDataGraphVariableBase.__init__(self, StructVariableTemplateHandler(self))

    def _loadChildrenFromGdb(self):
        StructVariable._loadChildrenFromGdb(self)
        self._setDataForChilds()
