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

""" @package stackmodel
A model that provides data about the GDB's call stack.
"""

from PyQt4.QtCore import Qt, QModelIndex, QAbstractTableModel
from operator import attrgetter


class StackModel(QAbstractTableModel):
    def __init__(self, controller, debugger, connector, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.connector = connector
        self.debugController = debugger
        self.controller = controller
        self.stack = []
        self.sortColumn = 0
        self.sortOrder = Qt.DescendingOrder

    def rowCount(self, parent):
        return len(self.stack)

    def columnCount(self, parent):
        return 4

    def data(self, index, role):
        assert(index.row() < len(self.stack))
        l = self.stack[index.row()]

        ret = None

        if role == Qt.DisplayRole:
            if index.column() == 0:
                if hasattr(l, "level"):
                    ret = str(l.level)
            elif index.column() == 1:
                if hasattr(l, "file"):
                    ret = l.file
            elif index.column() == 2:
                if hasattr(l, "func"):
                    ret = l.func
            elif index.column() == 3:
                if hasattr(l, "line"):
                    ret = l.line

        return ret

    def headerData(self, section, orientation, role):
        ret = None

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    ret = "Level"
                elif section == 1:
                    ret = "File"
                elif section == 2:
                    ret = "Function"
                elif section == 3:
                    ret = "Line"

        return ret

    def sort(self, column, order):
        self.sortColumn = column
        self.sortOrder = order

        rev = (order == Qt.AscendingOrder)

        if column == 0:
            key = 'level'
        elif column == 1:
            key = 'file'
        elif column == 2:
            key = 'func'
        elif column == 3:
            key = 'line'

        self.layoutAboutToBeChanged.emit()
        self.stack.sort(key=attrgetter(key), reverse=rev)
        self.layoutChanged.emit()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        ret = self.stack[row]

        return self.createIndex(row, column, ret)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def clear(self):
        self.layoutAboutToBeChanged.emit()
        self.stack = []
        self.layoutChanged.emit()

        self.controller.removeStackMarkers()

    def update(self):
        self.layoutAboutToBeChanged.emit()
        self.stack = self.connector.getStack()
        for s in self.stack:
            s.level = int(s.level)
        self.layoutChanged.emit()

        self.sort(self.sortColumn, self.sortOrder)
