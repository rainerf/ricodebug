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
from PyQt4.QtGui import QWidget, QTextCursor
from PyQt4.QtCore import QObject, SIGNAL

class PyIoView(QWidget):
    def __init__(self, debug_controller, parent = None):
        QWidget.__init__(self, parent)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.pyIoEdit = QtGui.QTextEdit(self)
        self.pyIoEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.pyIoEdit, 0, 0, 1, 2)
        
        self.pyInputEdit = QtGui.QComboBox(self)
        self.pyInputEdit.setEditable(True)
        self.gridLayout.addWidget(self.pyInputEdit, 1, 0, 1, 1)
        
        self.pySendButton = QtGui.QPushButton(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pySendButton.sizePolicy().hasHeightForWidth())
        self.pySendButton.setSizePolicy(sizePolicy)
        self.pySendButton.setText("Send")
        self.gridLayout.addWidget(self.pySendButton, 1, 1, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.debug_controller = debug_controller
        
        QObject.connect(self.pyInputEdit.lineEdit(), SIGNAL('returnPressed()'), self.pySendButton.click)
        QObject.connect(self.pySendButton, SIGNAL('clicked()'), self.executePythonCode)
        
    def executePythonCode(self):
        cmd = str(self.pyInputEdit.lineEdit().text())
        self.pyInputEdit.lineEdit().setText("")
        self.debug_controller.executePythonCode(cmd)

        # print the command in the IO edit
        s = "<font color=\"green\">"+cmd+"</font><br>\n"
        self.pyIoEdit.moveCursor(QTextCursor.End)
        self.pyIoEdit.insertHtml(s)
        self.pyIoEdit.moveCursor(QTextCursor.End)
