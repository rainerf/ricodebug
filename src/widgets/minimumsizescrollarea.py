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

from PyQt4.QtGui import QScrollArea, QVBoxLayout, QWidget, QFrame, QSizePolicy
from PyQt4.QtCore import QEvent

class MinimumSizeScrollArea(QScrollArea):
    def __init__(self, parent=None):
        QScrollArea.__init__(self, parent)
        self.s = 100
        self.setMinimumSize(0, 0)
        self.__max = 250
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        self.__w = QWidget()
        self.setWidget(self.__w)
        self.setWidgetResizable(True)
        self.__w.setLayout(QVBoxLayout())
        self.__w.layout().setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.NoFrame)
        self.__recalcSize()

    def sizeHint(self):
        return self.__w.layout().minimumSize()

    def __recalcSize(self):
        self.setMaximumSize(self.maximumSize().width(), min(self.__max, self.__w.layout().minimumSize().height()))

    def addWidget(self, widget):
        self.__w.layout().addWidget(widget)

    def event(self, e):
        if e.type() == QEvent.LayoutRequest:
            self.__recalcSize()
        return QScrollArea.event(self, e)