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
        return len(node._getChildren())

    def _getChildren(self):
        return self._getRootNodes()
