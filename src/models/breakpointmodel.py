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

from PyQt4.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant

from helpers.excep import GdbError
from helpers.icons import Icons


class AbstractBreakpoint(object):
    def __init__(self):
        self.addr = None
        self.condition = None
        self.skip = -1
        self.enabled = True
        self.number = -1
        self.times = None
        self.name = None
        self.fullname = None
        self.tooltip = None

    def fromGdbRecord(self, _):
        raise NotImplementedError()

    where = property(lambda: None)
    icon = property(lambda: None)


class Breakpoint(AbstractBreakpoint):
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
        AbstractBreakpoint.__init__(self)

        self.gdbConnector = connector
        self.file = None
        self.fullname = None
        self.func = None
        self.line = -1
        self.disp = None
        self.original_location = None
        self.type = None
        self.condition = "true"
        self.tooltip = "Breakpoint"

        if breakpoint:
            self.fromGdbRecord(breakpoint)

    icon = property(lambda self: Icons.bp if self.enabled else Icons.bp_dis)
    where = property(lambda self: "%s:%d" % (self.file, self.line))

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

        # check if it is a special multiple address breakpoint
        if rec.addr == "<MULTIPLE>":
            """ start special handling"""
            rec2 = self.gdbConnector.getMultipleBreakpoints(rec.number)
            self.parseOriginalLocation(rec2.__dict__['original-location'])
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


class BreakpointModel(QAbstractTableModel):
    LAYOUT = [('number', ''),
              ('enabled', ''),
              ('where', 'Where'),
              ('addr', 'Address'),
              ('condition', 'Condition'),
              ('skip', 'Skip'),
              ('times', 'Hits'),
              ('name', 'Name')]
    InternalDataRole = Qt.UserRole

    def __init__(self, do, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.breakpoints = []
        self.connector = do.gdb_connector
        do.signalProxy.cleanupModels.connect(self.clearBreakpoints)
        do.signalProxy.registerWithSessionManager.emit(self, "Breakpoints")
        do.signalProxy.breakpointModified.connect(self.__updateBreakpointFromGdbRecord)
        do.signalProxy.runClicked.connect(self.__resetHitCounters)

    def _newBreakpoint(self, breakpoint, connector, **kwargs):
        return Breakpoint(breakpoint, connector)

    def breakpointByLocation(self, fullname, line):
        """ search for breakpoint in file fullname on linenumber line
        @param fullname: (string), name of file
        @param line: (int), number of line
        @return: (bool), True if breakpoint found in list, False else
        """
        for bp in self.breakpoints:
            if bp.line == int(line) and bp.fullname == fullname:
                return bp
        return None

    def breakpointByNumber(self, number):
        """ search for breakpoint with given number
        @param number: (int), gdb's internal breakpoint number
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
        bp = self._newBreakpoint(res.bkpt, self.connector)

        self.beginInsertRows(QModelIndex(), len(self.breakpoints), len(self.breakpoints))
        self.breakpoints.append(bp)
        self.endInsertRows()

        return bp

    def toggleBreakpoint(self, fullname, line):
        """ toggles the breakpoint in file fullname with linenumber line
        @param fullname: (string), fullname of file
        @param line: (int), linenumber where the breakpoint should be toggled
        """
        if self.breakpointByLocation(fullname, line):
            self.deleteBreakpointByLocation(fullname, line)
            return None
        else:
            return self.insertBreakpoint(fullname, line)

    def deleteBreakpointByLocation(self, file_, line):
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
            self.__emitDataChangedForRows(row)

    def disableBreakpoint(self, number):
        """ disable breakpoint with number number
        @param number: (int), the number of breakpoint that should be disabled"""
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.disableBreakpoint(number)
            bp.enabled = False
            self.__emitDataChangedForRows(row)

    def setAllBreakpoints(self, enabled):
        """ set all breakpoints to enabled (enabled==True) or disabled (enabled==False)"""
        for bp in self.breakpoints:
            if enabled:
                self.connector.enableBreakpoint(bp.number)
            else:
                self.connector.disableBreakpoint(bp.number)
            bp.enabled = enabled
        self.__emitDataChangedForRows(0, len(self.breakpoints)-1)

    def changeCondition(self, number, condition):
        """ sets a condition condition to the specified breakpoint with number number
        @param number: (int), the number of breakpoint
        @param condition: (string), a condition like "var == 2" """
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.setConditionBreakpoint(number, condition)
            bp.condition = condition
            self.__emitDataChangedForRows(row)

    def changeSkip(self, number, skip):
        """ gdb will skip the breakpoint number number skip times
        @param number: (int), the number of breakpoint
        @param skip: (int), specifies how often breakpoint should be skipped"""
        row, bp = self.__findRowForNumber(number)
        if row is not None:
            self.connector.setSkipBreakpoint(number, skip)
            bp.skip = int(skip)
            self.__emitDataChangedForRows(row)

    def __updateBreakpointFromGdbRecord(self, rec):
        for info in rec.results:
            assert info.dest == "bkpt"
            row, bp = self.__findRowForNumber(int(info.src.number))
            if row is not None:
                bp.fromGdbRecord(info.src)
                self.__emitDataChangedForRows(row)

    def __resetHitCounters(self):
        for row, bp in enumerate(self.breakpoints):
            bp.times = 0
            self.__emitDataChangedForRows(row)

    def rowCount(self, parent):
        return len(self.breakpoints)

    def columnCount(self, parent):
        return len(self.LAYOUT)

    def data(self, index, role):
        assert(index.row() < len(self.breakpoints))

        ret = None

        column = index.column()

        bp = self.breakpoints[index.row()]

        if role == self.InternalDataRole:
            ret = bp
        elif role == Qt.DisplayRole:
            ret = getattr(bp, self.LAYOUT[column][0]) if self.LAYOUT[column][0] != 'enabled' else None
        elif role == Qt.CheckStateRole:
            if self.LAYOUT[column][0] == 'enabled':
                ret = Qt.Checked if bp.enabled else Qt.Unchecked
        elif role == Qt.DecorationRole:
            if self.LAYOUT[column][0] == 'number':
                ret = bp.icon
        elif role == Qt.ToolTipRole:
            if self.LAYOUT[column][0] == 'number':
                ret = bp.tooltip

        return ret

    def headerData(self, section, orientation, role):
        ret = None

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                ret = self.LAYOUT[section][1]
        return ret

    def flags(self, index):
        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        column = index.column()

        if self.LAYOUT[column][0] == 'enabled':
            f |= Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        elif self.LAYOUT[column][0] == 'condition':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif self.LAYOUT[column][0] == 'skip':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif self.LAYOUT[column][0] == 'name':
            f |= Qt.ItemIsEnabled | Qt.ItemIsEditable

        return f

    def __emitDataChangedForRows(self, first, last=None):
        if last is None:
            last = first
        firstIndex = self.index(first, 0, QModelIndex())
        secondIndex = self.index(last, self.columnCount(None) - 1, QModelIndex())
        self.dataChanged.emit(firstIndex, secondIndex)

    def setData(self, index, value, role):
        bp = self.breakpoints[index.row()]
        column = index.column()

        if self.LAYOUT[column][0] == 'condition':
            cond = str(value)
            if cond == "":
                cond = "true"
            try:
                self.changeCondition(bp.number, cond)
            except GdbError as e:
                logging.error("Could not set condition: %s", str(e))
                return False
        elif self.LAYOUT[column][0] == 'skip':
            try:
                skip = int(value)
            except ValueError:
                logging.error("Invalid _value for skip, must be an integer.")
                return False
            self.changeSkip(bp.number, skip)
        elif self.LAYOUT[column][0] == 'enabled':
            if role == Qt.CheckStateRole:
                if not value:
                    self.disableBreakpoint(bp.number)
                else:
                    self.enableBreakpoint(bp.number)
        elif self.LAYOUT[column][0] == 'name':
            bp.name = str(value)

            # make sure the view is updated
            self.__emitDataChangedForRows(index.row())

        return True

    def saveSession(self, xmlHandler):
        """Insert session info to xml file"""
        bpparent = xmlHandler.createNode("Breakpoints")
        for bp in self.getBreakpoints():
            xmlHandler.createNode("Breakpoint", bpparent, {"file": bp.file, "line": bp.line})

    def loadSession(self, xmlHandler):
        """load session info to xml file"""
        bpparent = xmlHandler.getNode("Breakpoints")
        if bpparent is not None:
            childnodes = bpparent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self.insertBreakpoint(attr["file"], attr["line"])
