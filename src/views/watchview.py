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
from PyQt4.QtGui import QTreeView, QMenu
from PyQt4.QtCore import Qt
from variables import filters
from controllers.treeitemcontroller import TreeStdVarWrapper


class TreeItemView(QTreeView):
    def __init__(self, controller, parent=None):
        QTreeView.__init__(self, parent)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.controller = controller
        self.expanded.connect(self.resizeColumn)

    def resizeColumn(self, _):
        """Resize the first column to contents when expanded."""
        self.resizeColumnToContents(0)


class WatchView(TreeItemView):
    def __init__(self, controller, parent=None):
        TreeItemView.__init__(self, controller, parent)

    def keyPressEvent(self, event):
        key = event.key()
        if (int(key) == Qt.Key_Delete):
            selectionModel = self.selectionModel()
            index = selectionModel.currentIndex()
            self.variableController.removeSelected(index.row(), index.parent())

    def contextMenuEvent(self, event):
        QTreeView.contextMenuEvent(self, event)
        if not event.isAccepted():
            selectionModel = self.selectionModel()
            wrapper = selectionModel.currentIndex().internalPointer()
            if isinstance(wrapper, TreeStdVarWrapper):
                menu = QMenu()
                filters.add_actions_for_all_filters(menu.addMenu("Set Filter for %s..." % wrapper.getExp()), wrapper)
                menu.exec_(event.globalPos())

