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
import logging
from helpers.excep import GdbError
from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, QObject
from PyQt4.QtGui import QPixmap

"""@package breakpointmodel
    there are some classes in this package:\n
    * BpInfo: a simple class that provides all really necessary information to select a breakpoint\n
    * ExtendedBreakpoint:     gdb breakpoints has some information like filename, line, ...
                            for special functionality there have to be more information like
                            name, condition, skip, ... This class extends the gdb breakpoints with
                            this informations\n

    * BreakpointModel: the model for breakpoints
"""


class ExtendedBreakpoint(QObject):
    """This class provides all members for basic gdb Breakpoint and extends it with
    more members like condition, name and interval.
    """
    def __init__(self, breakpoint, connector):
        """Initializes the Object.
        The breakPoint comes from gdb. Here it will be extended.
        @param breakPoint: type is a struct, provided from gdb, then parsed
        @param connector: type is GdbConnector, needed to communicate with gdb
        @note     there is a special case when creating breakpoints. for example if
                a breakpoint is set on end of a \"if{}\" and the \"}\" is the one
                and only symbol in this line it is possible that gdb returns a
                \"<MULTIPL>\" breakpoint address. in that case it is necessary to
                ask gdb via usual interface (not mi interface) for breakpoint information.
                parsing this information the address can be figured out.
        """

        QObject.__init__(self)

        self.gdbConnector = connector
        self.file = None
        self.fullname = None
        self.func = None
        self.line = -1

        self.addr = None
        self.disp = None
        self.enabled = None
        self.number = None
        self.original_location = None
        self.times = None
        self.type = None
        self.name = None
        self.condition = "true"
        self.skip = None

        if breakpoint:
            self.fromGdbRecord(breakpoint)

    def fromGdbRecord(self, rec):
        self.addr = rec.addr
        self.disp = rec.disp
        self.enabled = {"y": True, "n": False}[rec.enabled]
        self.number = int(rec.number)
        self.originalLocation = rec.__dict__['original-location']
        self.times = int(rec.times)
        self.type = rec.type
        if hasattr(rec, "cond"):
            self.condition = rec.cond
        self.skip = rec.ignore if hasattr(rec, "ignore") else 0

        """ proof if it is a special multiple address breakpoint"""
        if rec.addr == "<MULTIPLE>":
            """ start special handling"""
            self.multipleBreakPointInit(rec.number)
            self.parseOriginalLocation(rec.__dict__['original-location'])
            self.func = "unknown"
        else:
            self.file = getattr(rec, "file", "<unknown>")
            self.fullname = getattr(rec, "fullname", "<unknown>")
            self.func = getattr(rec, "func", None)
            if not self.func:
                self.func = getattr(rec, "at", None)
            self.line = int(getattr(rec, "line", "-1"))

    def parseOriginalLocation(self, origLoc):
        """ needed for special case of breakpoints <MULTIPLE> address"""
        origLoc = origLoc.split(':')
        self.fullname = origLoc[0]
        self.line = origLoc[1]
        origLoc = origLoc[0].split('/')
        self.file = origLoc[len(origLoc[0]) - 1]

    def multipleBreakPointInit(self, breakPointNumber):
        """ needed for special case of breakpoints <MULTIPLE> address"""
        self.gdbConnector.getMultipleBreakpoints(breakPointNumber)


class BreakpointModel(QAbstractTableModel):
    KEYS = ['number',
            'enabled',
            'file',
            'line',
            'addr',
            'condition',
            'skip',
            'times',
            'name']
    InternalDataRole = Qt.UserRole

    def __init__(self, do, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.breakpoints = []
        self.connector = do.gdb_connector
        do.signalProxy.cleanupModels.connect(self.clearBreakpoints)
        do.signalProxy.emitRegisterWithSessionManager(self, "Breakpoints")
        do.signalProxy.breakpointModified.connect(self.__updateBreakpointFromGdbRecord)
        do.signalProxy.runClicked.connect(self.__resetHitCounters)

        self.enabledBp = QPixmap(":/icons/images/bp.png")
        self.disabledBp = QPixmap(":/icons/images/bp_dis.png")

    def setBreakpoints(self, bpList):
        """ deletes all breakpoints in current list, and fill the list up with all breakpoints in bpList
        @param bpList: (List<Breakpoint>)
        """
        for bp in self.breakpoints:
            self.deleteBreakpoint(bp.fullname, bp.line)
        for bp in bpList:
            self.insertBreakpoint(bp.fullname, bp.line)

    def toggleBreakpoint(self, fullname, line):
        """ toggles the breakpoint in file fullname with linenumber line
        @param fullname: (string), fullname of file
        @param line: (int), linenumber where the breakpoint should be toggled
        """
        if self.isBreakpointByLocation(fullname, line):
            self.deleteBreakpoint(fullname, line)
            return None
        else:
            return self.insertBreakpoint(fullname, line)

    def isBreakpointByLocation(self, fullname, line):
        """ search for breakpoint in file fullname on linenumber line
        @param fullname: (string), name of file
        @param line: (int), number of line
        @return: (bool), True if breakpoint found in list, False else
        """
        for bp in self.breakpoints:
            if int(bp.line) == int(line) and bp.fullname == fullname:
                return bp
        return None

    def isBreakpointByNumber(self, number):
        """ search for breakpoint in file bpInfo.fullname on line bpInfo.line
        @param number: (int), gdb's internal breakpoint number
        @return: (bool), True if can find breakpoint in list, False else
        """
        for bp in self.breakpoints:
            if int(bp.number) == int(number):
                return bp
        return None

    def clearBreakpoints(self):
        """ deletes all breakpoints in list """
        # we need to store the numbers in a separate list since self.breakpoints
        # will be modified in the loop
        numbers = [bp.number for bp in self.breakpoints]
        for number in numbers:
            # delete breakpoints by number to avoid problems where the bp's file
            # name is unknown
            self.deleteBreakpointByNumber(number)

    def insertBreakpoint(self, file_, line):
        """ inserts a breakpoint in file file_ on linenumber line
        @param file_: (string), name of file
        @param line: (int), number of line
        @return (int), returns the real linenumber that gdb is choosing
        """
        res = self.connector.insertBreakpoint(file_, line)
        extendedBreakpoint = ExtendedBreakpoint(res.bkpt, self.connector)

        self.beginInsertRows(QModelIndex(), len(self.breakpoints), len(self.breakpoints))
        self.breakpoints.append(extendedBreakpoint)
        self.endInsertRows()

        return extendedBreakpoint

    def deleteBreakpoint(self, file_, line):
        """ deletes breakpoint in file file_ on linenumber line
        @param file_: (string), name of file
        @param line: (int), number of line
        """
        for bp in self.breakpoints:
            if bp.fullname == file_ and int(bp.line) == int(line):
                self.deleteBreakpointByNumber(bp.number)
                return
        else:
            logging.error("Cannot delete breakpoint (%s:%s) that is not in the model!", file_, line)

    def deleteBreakpointByNumber(self, number):
        """ deletes a breakpoint with a given number
        @param number: (int), number of the breakpoint to delete
        """
        for i, bp in enumerate(self.breakpoints):
            if bp.number == number:
                break
        else:
            logging.error("Cannot delete breakpoint (#%s) that is not in the model!", number)
            return

        self.connector.deleteBreakpoint(number)
        self.beginRemoveRows(QModelIndex(), i, i)
        self.breakpoints.remove(bp)
        self.endRemoveRows()

    def __findRowForNumber(self, number):
        for i, bp in enumerate(self.breakpoints):
            if bp.number == number:
                return i, bp
        else:
            return None, None

    def enableBreakpoint(self, number):
        """ enable breakpoint with number number
        @param number: (int), the number of breakpoint that should be enabled"""
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.enableBreakpoint(number)
            bp.enabled = True
            self.__emitDataChangedForRow(row)

    def disableBreakpoint(self, number):
        """ disable breakpoint with number number
        @param number: (int), the number of breakpoint that should be disabled"""
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.disableBreakpoint(number)
            bp.enabled = False
            self.__emitDataChangedForRow(row)

    def changeCondition(self, number, condition):
        """ sets a condition condition to the specified breakpoint with number number
        @param number: (int), the number of breakpoint
        @param condition: (string), a condition like "var == 2" """
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.setConditionBreakpoint(number, condition)
            bp.condition = condition
            self.__emitDataChangedForRow(row)

    def changeSkip(self, number, skip):
        """ gdb will skip the breakpoint number number skip times
        @param number: (int), the number of breakpoint
        @param skip: (int), specifies how often breakpoint should be skipped"""
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.setSkipBreakpoint(number, skip)
            bp.skip = int(skip)
            self.__emitDataChangedForRow(row)

    def __updateBreakpointFromGdbRecord(self, rec):
        for info in rec.results:
            assert info.dest == "bkpt"
            row, bp = self.__findRowForNumber(int(info.src.number))
            if row is not None:
                bp.fromGdbRecord(info.src)
                self.__emitDataChangedForRow(row)

    def __resetHitCounters(self):
        for row, bp in enumerate(self.breakpoints):
            bp.times = 0
            self.__emitDataChangedForRow(row)

    def rowCount(self, parent):
        return len(self.breakpoints)

    def columnCount(self, parent):
        return 9

    def data(self, index, role):
        assert(index.row() < len(self.breakpoints))

        ret = None

        column = index.column()

        bp = self.breakpoints[index.row()]

        if role == self.InternalDataRole:
            ret = bp
        elif role == Qt.DisplayRole:
            ret = getattr(bp, self.KEYS[column]) if self.KEYS[column] != 'enabled' else None
        elif role == Qt.CheckStateRole:
            if self.KEYS[column] == 'enabled':
                ret = Qt.Checked if bp.enabled else Qt.Unchecked
        elif role == Qt.DecorationRole:
            if self.KEYS[column] == 'number':
                ret = self.enabledBp if bp.enabled else self.disabledBp

        return ret

    def headerData(self, section, orientation, role):
        ret = None

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                ret = ["",  # Number
                       "",  # Enabled
                       "File",
                       "Line",
                       "Address",
                       "Condition",
                       "Skip",
                       "Hits",
                       "Name"][section]
        return ret

    def flags(self, index):
        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        column = index.column()

        if self.KEYS[column] == 'enabled':
            f |= Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        elif self.KEYS[column] == 'condition':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif self.KEYS[column] == 'skip':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif self.KEYS[column] == 'name':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable

        return f

    def __emitDataChangedForRow(self, row):
        firstIndex = self.index(row, 0, QModelIndex())
        secondIndex = self.index(row, self.columnCount(None) - 1, QModelIndex())
        self.dataChanged.emit(firstIndex, secondIndex)

    def setData(self, index, value, role):
        bp = self.breakpoints[index.row()]
        column = index.column()

        if self.KEYS[column] == 'condition':
            cond = str(value.toString())
            if cond == "":
                cond = "true"
            try:
                self.changeCondition(bp.number, cond)
            except GdbError as e:
                logging.error("Could not set condition: %s", str(e))
                return False
        elif self.KEYS[column] == 'skip':
            validSkip = QVariant(value).toInt()
            if not validSkip[1]:
                logging.error("Invalid value for skip, must be an integer.")
                return False
            self.changeSkip(bp.number, int(validSkip[0]))
        elif self.KEYS[column] == 'enabled':
            if role == Qt.CheckStateRole:
                if not QVariant(value).toBool():
                    self.disableBreakpoint(bp.number)
                else:
                    self.enableBreakpoint(bp.number)
        elif self.KEYS[column] == 'name':
            bp.name = str(value.toString())

            # make sure the view is updated
            self.__emitDataChangedForRow(index.row())

        return True

    def saveSession(self, xmlHandler):
        """Insert session info to xml file"""
        bpparent = xmlHandler.createNode("Breakpoints")
        for bp in self.getBreakpoints():
            xmlHandler.createNode("Breakpoint", bpparent, {"file": bp.file, "line": bp.line})

    def loadSession(self, xmlHandler):
        """load session info to xml file"""
        bpparent = xmlHandler.getNode("Breakpoints")
        if bpparent != None:
            childnodes = bpparent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self.insertBreakpoint(attr["file"], attr["line"])
