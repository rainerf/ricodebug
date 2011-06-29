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
from PyQt4.QtCore import SIGNAL, QObject, Qt

class WatchView(QWidget):
    def __init__(self, watch_controller, parent=None):
        QWidget.__init__(self, parent)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)
        
        self.treeView = QtGui.QTreeView(self)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.variableController = watch_controller
        
        QObject.connect(self.treeView, SIGNAL('expanded(QModelIndex)'), self.resizeColumn)
        
    def resizeColumn(self, index):
        """Resize the first column to contents when expanded."""
        self.treeView.resizeColumnToContents(0)
        
    def keyPressEvent (self, event ):
        key = event.key()
        if (int(key) == Qt.Key_Delete): #0x01000007
            selectionModel = self.treeView.selectionModel()
            index = selectionModel.currentIndex();
            self.variableController.removeSelected(index.row(), index.parent())
