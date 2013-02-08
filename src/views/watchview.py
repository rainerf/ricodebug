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

from PyQt4.QtCore import Qt
from views.treeitemview import TreeItemView
from variables import variable


class WatchView(TreeItemView):
    def __init__(self, do, parent=None):
        TreeItemView.__init__(self, do, parent)
        self.setAcceptDrops(True)

    def keyPressEvent(self, event):
        key = event.key()
        if (int(key) == Qt.Key_Delete):
            self.removeSelection()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(variable.MIME_TYPE):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, e):
        data = str(e.mimeData().data(variable.MIME_TYPE))
        self.model().addVar(data)

    def prepareContextMenu(self):
        menu = TreeItemView.prepareContextMenu(self)
        if self.selectionModel().currentIndex().parent().internalPointer() is None:
            menu.addAction("Remove variable").triggered.connect(
                    self.removeSelection)
        return menu

    def removeSelection(self):
        index = self.selectionModel().currentIndex()
        self.model().removeRows(index.row(), 1, index.parent())
