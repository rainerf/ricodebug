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

from PyQt4.QtCore import QObject, Qt
from views.mitraceview import MiTraceView
from helpers.gdboutput import GdbOutput


class MiTraceController(QObject):
    def __init__(self, distributedObjects):
        QObject.__init__(self)
        self.__do = distributedObjects

        self.__view = MiTraceView()

        self.__do.mainwindow.insertDockWidget(self.__view, "MI Trace", Qt.BottomDockWidgetArea, True)
        self.__do.gdb_connector.commandExecuted.connect(self.appendCommand)
        self.__do.gdb_connector.reader.asyncRecordReceived.connect(self.appendAsync)

    def appendCommand(self, cmd, rec):
        self.__view.append("<b>" + cmd + "</b>")
        color = 'color="#ff3333"' if rec.class_ == GdbOutput.ERROR else ""
        self.__view.append("<font %s>%s</font>" % (color, rec.raw))

    def appendAsync(self, rec):
        self.__view.append('<font color="#777777">%s</font>' % rec.raw)
