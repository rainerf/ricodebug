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

from PyQt4.QtGui import QWidget

from .ui_scriptview import Ui_ScriptView


class ScriptView(QWidget):
    def __init__(self, do, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_ScriptView()
        self.ui.setupUi(self)

        self.ui.transcript.init(do)
        self.do = do

        self.ui.input.lineEdit().returnPressed.connect(self.ui.sendButton.click)
        self.ui.sendButton.clicked.connect(self.executePythonCode)

    def executePythonCode(self):
        cmd = str(self.ui.input.lineEdit().text())
        self.ui.input.lineEdit().setText("")
        self.do.scriptEnv.exec_(cmd)

    def appendTranscript(self, t):
        self.ui.transcript.append(t+"\n")
