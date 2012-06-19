from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt4.QtGui import QPixmap


class ThreadInfo:
    STOPPED, RUNNING = range(2)

    def __init__(self, id_):
        self.frame = None
        self.id = id_
        self.core = None
        self.name = None
        self.state = None

    def updateFromGdb(self, res):
        self.core = res.core
        self.name = res.name
        self.state = {"stopped": self.STOPPED, "running": self.RUNNING}[res.state]
        self.frame = res.frame


class ThreadModel(QAbstractTableModel):
    def __init__(self, distributedObjects):
        QAbstractTableModel.__init__(self)
        self.__do = distributedObjects
        self.__threads = []
        self.__do.signalProxy.inferiorStoppedNormally.connect(self.update)
        self.__do.signalProxy.threadCreated.connect(self.threadCreated)
        self.__do.signalProxy.threadExited.connect(self.threadExited)

        self.__currentThread = None

        self.threadRunningPixmap = QPixmap(":/icons/images/16x16/running.png")
        self.threadStoppedPixmap = QPixmap(":/icons/images/16x16/stopped.png")

    def __addThread(self, id_):
        self.beginInsertRows(QModelIndex(), len(self.__threads), len(self.__threads))
        t = ThreadInfo(id_)
        self.__threads.append(t)
        self.endInsertRows()

    def __removeThread(self, id_):
        for i, t in enumerate(self.__threads):
            if t.id == id_:
                break

        self.beginRemoveRows(QModelIndex(), i, i)
        del self.__threads[i]
        self.endRemoveRows()

    def update(self):
        res = self.__do.gdb_connector.threadInfo()
        for ti in res.threads:
            for i, t in enumerate(self.__threads):
                if ti.id == t.id:
                    # update the entry
                    t.updateFromGdb(ti)

                    # update the views
                    firstIndex = self.index(i, 0, QModelIndex())
                    secondIndex = self.index(i, self.columnCount(None), QModelIndex())
                    self.dataChanged.emit(firstIndex, secondIndex)
                    break

        self.__currentThread = getattr(res, "current-thread-id")

    def clear(self):
        self.__threads = []
        self.reset()

    def rowCount(self, _):
        return len(self.__threads)

    def columnCount(self, _):
        return 7

    def data(self, index, role):
        if not index.isValid():
            return None

        t = self.__threads[index.row()]
        c = index.column()

        res = None

        if role == Qt.DisplayRole:
            if c == 0:
                res = t.id
            elif c == 1:
                res = t.core
            elif c == 2:
                res = t.name
            elif c == 3:
                if t.state == ThreadInfo.RUNNING:
                    res = "Running"
                elif t.state == ThreadInfo.STOPPED:
                    res = "Stopped"
                if t.id == self.__currentThread:
                    res += ", Active"
            elif c == 4:
                res = t.frame.func
            elif c == 5:
                res = t.frame.line
            elif c == 6:
                res = t.frame.level
        elif role == Qt.DecorationRole:
            if c == 3:
                if t.state == ThreadInfo.RUNNING:
                    res = self.threadRunningPixmap
                elif t.state == ThreadInfo.STOPPED:
                    res = self.threadStoppedPixmap

        return res

    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None

        if role == Qt.DisplayRole:
            return {0: "ID", 1: "Core", 2: "Name", 3: "State", 4: "Function", 5: "Line", 6: "Level"}[section]

    def threadCreated(self, rec):
        for r in rec.results:
            if r.dest == "id":
                self.__addThread(r.src)

    def threadExited(self, rec):
        for r in rec.results:
            if r.dest == "id":
                self.__removeThread(r.src)
