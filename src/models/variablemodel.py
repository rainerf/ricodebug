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

from PyQt4.QtCore import QAbstractItemModel, Qt, QModelIndex, QStringList, QMimeData
from PyQt4.QtGui import QPixmap, QBrush, QPainter


from variables.ptrvariable import PtrVariable
from variables.structvariable import StructVariable
from variables.arrayvariable import ArrayVariable
from variables.stdvariable import StdVariable
from variables.variablelist import VariableList
from variables import variable
import logging


class NodeBase(object):
    def __init__(self):
        self._row = None
        self._parent = None
        self._model = None

    def setNodeData(self, row, parent, model):
        self._row = row
        self._parent = parent
        self._model = model

    def _childCount(self):
        raise NotImplementedError()

    def _child(self, i):
        raise NotImplementedError()

    def _hasChildren(self):
        return False

    def _index(self, column):
        if self._parent:
            pi = self._parent._index(0)
        else:
            pi = QModelIndex()
        return self._model.index(self._row, column, pi)


class TreeVariableBase(NodeBase):
    def __init__(self):
        NodeBase.__init__(self)
        self.marked = False
        self.changed.connect(self.markAndNotifyModel)

    def _child(self, i):
        return self.childs[i]

    def _setNodeDataForChilds(self):
        for row, c in enumerate(self.childs):
            c.setNodeData(row, self, self._model)

    def _notifyModel(self):
        self._model.emitDataChanged(self._index(2), self._index(2))

    def markAndNotifyModel(self):
        self.marked = True
        self._notifyModel()

    def unmarkAll(self):
        for i in self._childs:
            i.unmarkAll()

        if self.marked:
            self.marked = False
            self._notifyModel()


class TreePtrVariable(PtrVariable, TreeVariableBase):
    def __init__(self, *args):
        PtrVariable.__init__(self, *args)
        TreeVariableBase.__init__(self)

        self._valid = self._pointerValid()

    def _childCount(self):
        return 1 if self._valid else 0

    def _loadChildrenFromGdb(self):
        PtrVariable._loadChildrenFromGdb(self)
        self._setNodeDataForChilds()

    def _hasChildren(self):
        return self._valid

    def markAndNotifyModel(self):
        if self._pointerValid() and not self._valid:
            self._model.beginInsertRows(self._index(0), 0, 0)
            self._valid = True
            self._model.endInsertRows()
        elif not self._pointerValid() and self._valid:
            self._model.beginRemoveRows(self._index(0), 0, 0)
            self._valid = False
            self._model.endRemoveRows()
        TreeVariableBase.markAndNotifyModel(self)


class TreeStructVariable(StructVariable, TreeVariableBase):
    def __init__(self, *args):
        StructVariable.__init__(self, *args)
        TreeVariableBase.__init__(self)

    def _childCount(self):
        return len(self.childs)

    def _loadChildrenFromGdb(self):
        StructVariable._loadChildrenFromGdb(self)
        self._setNodeDataForChilds()

    def _hasChildren(self):
        return True


class TreeArrayVariable(ArrayVariable, TreeVariableBase):
    def __init__(self, *args):
        ArrayVariable.__init__(self, *args)
        TreeVariableBase.__init__(self)

    def _childCount(self):
        return len(self.childs)

    def _loadChildrenFromGdb(self):
        ArrayVariable._loadChildrenFromGdb(self)
        self._setNodeDataForChilds()

    def _hasChildren(self):
        return True


class TreeStdVariable(StdVariable, TreeVariableBase):
    def __init__(self, *args):
        StdVariable.__init__(self, *args)
        TreeVariableBase.__init__(self)

    def _childCount(self):
        return 0

    def _child(self, i):
        raise ValueError("StdVariable does not have any childs.")


class TreeVariableFactory:
    StdVariable = TreeStdVariable
    ArrayVariable = TreeArrayVariable
    PtrVariable = TreePtrVariable
    StructVariable = TreeStructVariable


class VariableModel(QAbstractItemModel):
    def __init__(self, do, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._vars = VariableList(TreeVariableFactory, do)

        do.signalProxy.cleanupModels.connect(self.clear)
        do.signalProxy.aboutToUpdateVariables.connect(self.__unmarkAll)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = parent.internalPointer() if parent.isValid() else None
        if parentItem:
            childItem = parentItem._child(row)
        else:
            childItem = self._vars[row]

        return self.createIndex(row, column, childItem)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem._parent

        if not parentItem:
            return QModelIndex()

        return self.createIndex(parentItem._row, 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            return len(self._vars)
        else:
            return parent.internalPointer()._childCount()

    def columnCount(self, _):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        ret = None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                ret = item.exp
            elif index.column() == 1:
                ret = item.type
            elif index.column() == 2:
                ret = item.value

        elif role == Qt.EditRole:
            if index.column() == 2:
                ret = item.value

        elif role == Qt.DecorationRole:
            if index.column() == 0:
                if item.access in ['private', 'protected']:
                    iconprefix = item.access + "_"
                else:
                    iconprefix = ""

                icon = None
                if not item.inScope:
                    return QPixmap(":/icons/images/outofscope.png")
                elif not isinstance(item, StdVariable):
                    icon = QPixmap(":/icons/images/" + iconprefix + "struct.png")
                else:  # leave item
                    icon = QPixmap(":/icons/images/" + iconprefix + "var.png")

                # overlay for arguments
                if icon and item.arg:
                    ol = QPixmap(":/icons/images/overlay_arg.png")
                    p = QPainter(icon)
                    p.drawPixmap(ol.rect(), ol)
                elif icon and item.exp == "Return value":
                    ol = QPixmap(":/icons/images/overlay_ret.png")
                    p = QPainter(icon)
                    p.drawPixmap(ol.rect(), ol)
                return icon

        elif role == Qt.BackgroundRole:
            if not item.inScope:
                ret = QBrush(Qt.gray)
            elif index.column() == 2:
                if item.marked and item.inScope:
                    ret = QBrush(Qt.yellow)

        return ret

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Expression", "Type", "Value"][section]
        return None

    def addVar(self, name):
        self.beginInsertRows(QModelIndex(), len(self._vars), len(self._vars))
        var = self._vars.addVarByName(name)
        var.setNodeData(len(self._vars) - 1, None, self)
        self.endInsertRows()
        return var

    def hasChildren(self, parent):
        if not parent.isValid():
            return True

        return parent.internalPointer()._hasChildren()

    def emitDataChanged(self, tl, br):
        self.dataChanged.emit(tl, br)

    def mimeTypes(self):
        return QStringList([variable.MIME_TYPE])

    def mimeData(self, indexes):
        if len(indexes) == 1:
            item = indexes[0].internalPointer()
            d = QMimeData()
            d.setData(variable.MIME_TYPE, item.uniqueName)
            return d
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        item = index.internalPointer()
        if not item.inScope:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        ret = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if index.column() == 2:
            ret |= Qt.ItemIsEditable
        elif index.column() == 0:
            ret |= Qt.ItemIsDragEnabled

        return ret

    def removeVar(self, var):
        pos = self._vars._vars.index(var)
        self.removeRows(pos, 1, QModelIndex())

    def removeRows(self, position, rows, parent):
        """ removes the selected row in the model
        @param position   int, starting position of selection
        @param rows       int, number of rows to delete beginning at starting position
        @param parent     TreeItem, parent item containing items to delete
        """
        parentItem = parent.internalPointer()
        if parentItem:
            logging.error("Cannot remove a child variable.")
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in xrange(position, position + rows):
            self._vars.removeIdx(i)

        # fix the _row members of the remaining elements
        for offset, var in enumerate(self._vars[position:]):
            var._row = position + offset
        self.endRemoveRows()
        return True

    def clear(self):
        self.beginResetModel()
        self._vars.clear()
        self.endResetModel()

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            index.internalPointer().assignValue(value.toString())
            return True
        return False

    def __unmarkAll(self):
        for i in self._vars._vars:
            i.unmarkAll()
