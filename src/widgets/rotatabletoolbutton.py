# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2012  he ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# Copyright (C) 2005 - 2011  Filipe AZEVEDO & The Monkey Studio Team
# http://monkeystudio.org licensing under the GNU GPL.
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

from PyQt4.QtGui import QToolButton, QBoxLayout, QPixmap, QColor, \
        QStyleOptionToolButton, QPainter, QStyle
from PyQt4.QtCore import QPoint


class RotatableToolButton(QToolButton):
    def __init__(self, parent, direction):
        QToolButton.__init__(self, parent)
        self.direction = None
        self.setDirection(direction)

    def paintEvent(self, _):
        s = QToolButton.sizeHint(self)
        r = 0
        p = QPoint()

        if self.direction == QBoxLayout.TopToBottom:
            r = 90
            p = QPoint(0, -s.height())
        elif self.direction == QBoxLayout.BottomToTop:
            r = -90
            p = QPoint(-s.width(), 0)

        pixmap = QPixmap(s)
        pixmap.fill(QColor(0, 0, 0, 0))

        o = QStyleOptionToolButton()
        self.initStyleOption(o)

        o.rect.setSize(s)

        pixpainter = QPainter()
        pixpainter.begin(pixmap)
        self.style().drawComplexControl(QStyle.CC_ToolButton, o, pixpainter, self)
        pixpainter.end()

        painter = QPainter(self)
        painter.rotate(r)
        painter.drawPixmap(p, pixmap)

    def sizeHint(self):
        s = QToolButton.sizeHint(self)

        if self.direction in [QBoxLayout.TopToBottom, QBoxLayout.BottomToTop]:
            s.transpose()

        return s

    def setDirection(self, direction):
        self.direction = direction
        self.update()
