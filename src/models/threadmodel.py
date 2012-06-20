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

from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt4.QtGui import QPixmap
from operator import attrgetter


class ThreadInfo:
    STOPPED, RUNNING = range(2)

    def __init__(self, id_):
        self.id = id_
        self.core = None
        self.name = None
        self.state = None
        self.file = None
        self.func = None
        self.line = None
        self.level = None

    def updateFromGdb(self, res):
        self.core = res.core
        self.name = res.name
        self.state = {"stopped": self.STOPPED, "running": self.RUNNING}[res.state]
        self.file = None
        try:
            self.file = res.frame.file
            self.file = res.frame.fullname
        except AttributeError:
            pass
        self.func = res.frame.func
        self.line = res.frame.line
        self.level = res.frame.level


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
        self.currentTheadPixmap = QPixmap(":/icons/images/arrow-right.png")

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
        return 8

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
            elif c == 4:
                res = t.file
            elif c == 5:
                res = t.func
            elif c == 6:
                res = t.line
            elif c == 7:
                res = t.level
        elif role == Qt.DecorationRole:
            if c == 0:
                if t.id == self.__currentThread:
                    res = self.currentTheadPixmap
            elif c == 3:
                if t.state == ThreadInfo.RUNNING:
                    res = self.threadRunningPixmap
                elif t.state == ThreadInfo.STOPPED:
                    res = self.threadStoppedPixmap
        elif role == Qt.TextAlignmentRole:
            if c == 0:
                res = Qt.AlignRight | Qt.AlignVCenter
        elif role == Qt.ToolTipRole:
            if c == 0:
                if t.id == self.__currentThread:
                    res = "Current Thread"
            elif c == 3:
                if t.state == ThreadInfo.RUNNING:
                    res = "Running"
                elif t.state == ThreadInfo.STOPPED:
                    res = "Stopped"

        return res

    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None

        if role == Qt.DisplayRole:
            return {0: "ID", 1: "Core", 2: "Name", 3: "State", 4: "File", 5: "Function", 6: "Line", 7: "Level"}[section]

    def sort(self, column, order):
        self.sortColumn = column
        self.sortOrder = order

        rev = (order == Qt.AscendingOrder)

        key = {0: "id", 1: "core", 2: "name", 3: "state", 4: "file", 5: "func", 6: "line", 7: "level"}[column]

        self.layoutAboutToBeChanged.emit()
        self.__threads.sort(key=attrgetter(key), reverse=rev)
        self.layoutChanged.emit()

    def threadCreated(self, rec):
        for r in rec.results:
            if r.dest == "id":
                self.__addThread(r.src)

    def threadExited(self, rec):
        for r in rec.results:
            if r.dest == "id":
                self.__removeThread(r.src)

    def threadIdForRow(self, row):
        return self.__threads[row].id
