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
from PyQt4.QtCore import QModelIndex

from helpers.icons import Icons
from models.breakpointmodel import BreakpointModel, AbstractBreakpoint


class Watchpoint(AbstractBreakpoint):
    def __init__(self, res, exp, addr):
        AbstractBreakpoint.__init__(self)
        self.exp = exp
        self.addr = addr
        self.condition = "true"
        self.skip = 0
        self.number = int(res.wpt.number)

        self.tooltip = "Watchpoint"

    where = property(lambda self: self.exp)
    icon = property(lambda self: Icons.wp if self.enabled else Icons.wp_dis)

    def fromGdbRecord(self, rec):
        pass


class StoppointModel(BreakpointModel):
    def insertWatchpoint(self, exp):
        addr = self.connector.evaluate("&" + exp)
        res = self.connector.insertWatchpoint("*" + addr)
        bp = Watchpoint(res, exp, addr)

        self.beginInsertRows(QModelIndex(), len(self.breakpoints), len(self.breakpoints))
        self.breakpoints.append(bp)
        self.endInsertRows()
