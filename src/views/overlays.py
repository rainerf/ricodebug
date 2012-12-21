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

from PyQt4.QtGui import QPixmap, QLabel, QFrame, QHBoxLayout, QColor
from PyQt4.QtCore import Qt
from helpers.clickablelabel import ClickableLabel


class OverlayWidget(QFrame):
    def __init__(self, parent, color2):
        QFrame.__init__(self, parent)
        layout = QHBoxLayout(self)
        layout.setMargin(0)
        color1 = QColor(color2).lighter(110).name()
        self.setStyleSheet("QFrame { background-color : qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 1 %s); }" % (color1, color2))

    def update(self):
        raise NotImplementedError()


class BreakpointOverlayWidget(OverlayWidget):
    color = "#ff8080"

    def __init__(self, parent, bp, bpModel):
        OverlayWidget.__init__(self, parent, self.color)
        self.markerBp = QPixmap(":/markers/bp.png")
        self.markerBpDisabled = QPixmap(":/markers/bp_dis.png")
        self.bp = bp
        self.__bpModel = bpModel
        self.__icon = ClickableLabel()
        self.__icon.clicked.connect(self.toggleEnabled)
        self.__text = QLabel()

        self.layout().addWidget(self.__icon, 0)
        self.layout().addWidget(self.__text, 0)
        self.__icon.setCursor(Qt.ArrowCursor)

    def update(self):
        if self.bp.name:
            self.__text.setText("Breakpoint '%s', hit %s times" % (self.bp.name, self.bp.times))
        else:
            self.__text.setText("Breakpoint #%s, hit %s times" % (self.bp.number, self.bp.times))
        self.__icon.setPixmap(self.markerBp if self.bp.enabled else self.markerBpDisabled)
        self.resize(self.sizeHint().width(), self.height())

    def toggleEnabled(self):
        if self.bp.enabled:
            self.__bpModel.disableBreakpoint(self.bp.number)
        else:
            self.__bpModel.enableBreakpoint(self.bp.number)
