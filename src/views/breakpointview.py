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

from PyQt4 import QtGui
from PyQt4.QtGui import QTableView


class BreakpointView(QTableView):
    def __init__(self, do, parent=None):
        QTableView.__init__(self, parent)

        self.do = do
        self.doubleClicked.connect(self.onDoubleClicked)

        self.setTabKeyNavigation(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(20)
        self.horizontalHeader().setStretchLastSection(True)

    def onDoubleClicked(self, index):
        bp = self.model().breakpoints[index.row()]
        self.do.signalProxy.openFile(bp.fullname, int(bp.line))

