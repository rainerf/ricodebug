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

from PyQt4.QtGui import QWidget, QGridLayout, QTextEdit, QComboBox, QPushButton, QSizePolicy


class PyIoView(QWidget):
    def __init__(self, do, parent=None):
        QWidget.__init__(self, parent)

        layout = QGridLayout(self)
        layout.setMargin(0)

        self.__pyIoEdit = QTextEdit(self)
        self.__pyIoEdit.setReadOnly(True)
        layout.addWidget(self.__pyIoEdit, 0, 0, 1, 2)

        self.__pyInputEdit = QComboBox(self)
        self.__pyInputEdit.setEditable(True)
        layout.addWidget(self.__pyInputEdit, 1, 0, 1, 1)

        self.__sendButton = QPushButton(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.__sendButton.sizePolicy().hasHeightForWidth())
        self.__sendButton.setSizePolicy(sizePolicy)
        self.__sendButton.setText("Send")
        layout.addWidget(self.__sendButton, 1, 1, 1, 1)

        self.do = do

        self.__pyInputEdit.lineEdit().returnPressed.connect(self.__sendButton.click)
        self.__sendButton.clicked.connect(self.executePythonCode)

    def executePythonCode(self):
        cmd = str(self.__pyInputEdit.lineEdit().text())
        self.__pyInputEdit.lineEdit().setText("")
        self.do.scriptEnv.exec_(cmd)

    def appendTranscript(self, t):
        self.__pyIoEdit.append(t)
