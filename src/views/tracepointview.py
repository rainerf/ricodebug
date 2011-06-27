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

class TracepointView(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.tracepointView = QtGui.QTableView(self)
        self.tracepointView.setTabKeyNavigation(False)
        self.tracepointView.setAlternatingRowColors(True)
        self.tracepointView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tracepointView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tracepointView.setShowGrid(False)
        self.tracepointView.setSortingEnabled(True)
        self.tracepointView.setCornerButtonEnabled(False)
        self.tracepointView.verticalHeader().setVisible(False)
        self.tracepointView.verticalHeader().setDefaultSectionSize(20)
        self.tracepointView.horizontalHeader().setStretchLastSection(True)
        self.tracepointView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.gridLayout.addWidget(self.tracepointView, 0, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)
        
    def getSelectedRow(self):
        if len(self.tracepointView.selectionModel().selectedIndexes()) > 0:
            return self.tracepointView.selectionModel().selectedIndexes()[0]
        return None
