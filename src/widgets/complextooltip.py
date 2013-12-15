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

from PyQt4.QtCore import Qt, QTimer, pyqtSignal
from PyQt4.QtGui import QWidget, QStylePainter, QStyleOptionFrame, QStyle, QToolTip

class ComplexToolTip(QWidget):
    hidden = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setPalette(QToolTip.palette())
        self.setStyleSheet("QLabel {color: white}")

        self.__hideTimer = QTimer()
        self.__hideTimer.setSingleShot(True)
        self.__hideTimer.timeout.connect(self.hideNow)

        self.__allowHide = True
        self.hide()

    def hideNow(self):
        if self.__allowHide:
            QWidget.hide(self)
            self.hidden.emit()

    def setDisallowHide(self, x):
        self.__allowHide = not x

    def enterEvent(self, _):
        self.__hideTimer.stop()

    def hideLater(self):
        self.__hideTimer.start(250)

    # hide the widget when the mouse leaves it
    def leaveEvent(self, _):
        self.hideLater()

    def paintEvent(self, e):
        QWidget.paintEvent(self, e)
        # this makes the tool tip use the system's tool tip color as its background
        painter = QStylePainter(self)
        opt = QStyleOptionFrame()
        opt.initFrom(self)
        painter.drawPrimitive(QStyle.PE_PanelTipLabel, opt)

    def showToolTip(self, pos, parent):
        self.move(parent.mapToGlobal(pos))
        self.raise_()
        self.show()
