# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# Based on work by:
# Copyright (C) 2009  Virgil Dupras
# http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel
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

from PyQt4.QtCore import QAbstractItemModel, QModelIndex


class TreeNode:
    def __init__(self, parent, model):
        self.parent = parent
        self.model = model

    def _getChildren(self):
        raise NotImplementedError()

    def _getColumnCount(self):
        raise NotImplementedError()

    def _rowInParent(self):
        if self.parent:
            return self.parent._getChildren().index(self)
        else:
            return self.model._getRootNodes().index(self)

    def _rowCount(self):
        raise NotImplementedError()

    def _index(self, column=0):
        if self.parent:
            pi = self.parent._index()
        else:
            pi = QModelIndex()
        return self.model.index(self._rowInParent(), column, pi)


class TreeModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)

    def _getRootNodes(self):
        raise NotImplementedError()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self._getRootNodes()[row])
        parentNode = parent.internalPointer()
        return self.createIndex(row, column, parentNode._getChildren()[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent._rowInParent(), 0, node.parent)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self._getRootNodes())
        node = parent.internalPointer()

        # of the node knows how many rows it has, use that value; otherwise,
        # count them ourselves
        try:
            return node._rowCount()
        except NotImplementedError:
            return len(node._getChildren())

    def _getChildren(self):
        return self._getRootNodes()
