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

from PyQt4.QtGui import QPixmap, QLabel, QFrame, QHBoxLayout, QColor, QPainter, QPolygon, QPen, QLinearGradient
from PyQt4.QtCore import Qt, QPoint, QSize
from helpers.clickablelabel import ClickableLabel


class PointyLabel(QLabel):
    def __init__(self, parent, color1, color2):
        QLabel.__init__(self, parent)
        self.resize(self.sizeHint())
        self.setStyleSheet("QLabel { background-color: rgba(0, 0, 0, 0) }")
        self.color1 = QColor(color1)
        self.color2 = QColor(color2)

    def sizeHint(self):
        return QSize(10, 10)

    def paintEvent(self, _):
        p = QPainter(self)
        points = [QPoint(self.width(), -1), QPoint(self.width(), self.height()),
                  QPoint(0, self.height() / 2), QPoint(0, self.height() / 2 - 1)]
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, self.color1)
        grad.setColorAt(1, self.color2)
        p.setBrush(grad)
        p.setPen(QPen(Qt.NoPen))
        p.drawPolygon(QPolygon(points))


class OverlayWidget(QFrame):
    def __init__(self, parent, color2):
        QFrame.__init__(self, parent)
        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        color1 = QColor(color2).lighter(150).name()
        layout.addWidget(PointyLabel(self, color1, color2))
        self.setStyleSheet("QLabel { background-color : QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 1 %s) }" % (color1, color2))

    def update(self):
        raise NotImplementedError()


class BreakpointOverlayWidget(OverlayWidget):
    color = "#ff6060"

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
