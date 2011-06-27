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

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import QObject, SIGNAL

class BreakpointView(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.breakpointView = QtGui.QTableView(self)
        self.breakpointView.setTabKeyNavigation(False)
        self.breakpointView.setAlternatingRowColors(True)
        self.breakpointView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.breakpointView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.breakpointView.setShowGrid(False)
        self.breakpointView.setSortingEnabled(True)
        self.breakpointView.setCornerButtonEnabled(False)
        self.breakpointView.verticalHeader().setVisible(False)
        self.breakpointView.verticalHeader().setDefaultSectionSize(20)
        self.breakpointView.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.breakpointView, 0, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)
        
