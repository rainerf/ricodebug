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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QTextCursor
from .stylesheets import STYLESHEET
from helpers.tools import unBackslashify
from helpers.gdboutput import GdbOutput


class GdbIoView(QWidget):
    def __init__(self, debug_controller, parent=None):
        QWidget.__init__(self, parent)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.gdbInputEdit = QtGui.QComboBox(self)
        self.gdbInputEdit.setEditable(True)
        self.gridLayout.addWidget(self.gdbInputEdit, 2, 0, 1, 1)

        self.gdbSendButton = QtGui.QPushButton(self)
        self.gdbSendButton.setText("Send")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gdbSendButton.sizePolicy().hasHeightForWidth())
        self.gdbSendButton.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.gdbSendButton, 2, 1, 1, 1)

        self.gdbIoEdit = QtGui.QTextEdit(self)
        self.gdbIoEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gdbIoEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.gdbIoEdit, 1, 0, 1, 2)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.debugController = debug_controller
        self.gdbInputEdit.lineEdit().returnPressed.connect(self.gdbSendButton.click)
        self.gdbSendButton.clicked.connect(self.executeCliCommand)
        self.debugController.connector.reader.consoleRecordReceived.connect(
                self.handleConsoleRecord, Qt.QueuedConnection)

    def executeCliCommand(self):
        cmd = str(self.gdbInputEdit.lineEdit().text())
        self.gdbInputEdit.lineEdit().setText("")
        res = self.debugController.executeCliCommand(cmd)

        # print the command in the IO edit
        s = STYLESHEET + "<span class=\"gdbconsole_output_ok\">" + cmd + "</span><br>\n"
        if res:
            s += "<span class=\"gdbconsole_output_error\">" + unBackslashify(res) + "</span><br>\n"
        self.gdbIoEdit.moveCursor(QTextCursor.End)
        self.gdbIoEdit.insertHtml(s)
        self.gdbIoEdit.moveCursor(QTextCursor.End)

    def handleConsoleRecord(self, rec):
        if rec.type_ == GdbOutput.CONSOLE_STREAM:
            self.gdbIoEdit.moveCursor(QTextCursor.End)
            s = unBackslashify(rec.string)
            self.gdbIoEdit.insertPlainText(s)
            self.gdbIoEdit.moveCursor(QTextCursor.End)

