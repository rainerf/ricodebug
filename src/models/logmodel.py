from PyQt4.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt4.QtGui import QSortFilterProxyModel
from operator import attrgetter

class LogModel(QAbstractTableModel):
    def __init__(self, parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.records = []
        
    def rowCount(self, parent):
        return len(self.records)
    
    def columnCount(self, parent):
        return 6

    def data(self, index, role):
        assert(index.row() < len(self.records))
        record = self.records[index.row()]
        
        ret = None

        if role == Qt.DisplayRole:
            if index.column() == 0:
                ret = "%0.3f" % (record.relativeCreated / 1000)
            elif index.column() == 1:
                ret = record.levelno
            elif index.column() == 2:
                ret = record.message
            elif index.column() == 3:
                ret = record.funcName
            elif index.column() == 4:
                ret = record.filename
            elif index.column() == 5:
                ret = record.lineno

        return ret
    
    def headerData(self, section, orientation, role):
        if section < 6 and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Time", "Level", "Message", "Function", "File", "Line"][section]
        else:
            return None
    
#    def sort(self, column, order):
#        rev = (order == Qt.AscendingOrder)
#
#        key = ["relativeCreated", "levelno", "message", "funcName", "filename", "lineno"][column]
#
#        self.emit(SIGNAL('layoutAboutToBeChanged()'))
#        self.records.sort(key=attrgetter(key), reverse=rev)
#        self.emit(SIGNAL('layoutChanged()'))
        
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex();
        
        ret = self.records[row]
            
        return self.createIndex(row, column, ret)
    
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertMessage(self, record):
        self.beginInsertRows(QModelIndex(), len(self.records), len(self.records))
        self.records.append(record)
        self.endInsertRows()
    
class FilteredLogModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.setDynamicSortFilter(True)
        self.minimum = 0
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        data = self.sourceModel().index(sourceRow, 1, sourceParent).data().toInt()[0]
        return data >= self.minimum
    
    def setMinimum(self, minimum):
        self.minimum = minimum
        self.invalidateFilter()