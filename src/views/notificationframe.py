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

import logging
from PyQt4.QtGui import QApplication, QStyle, QColor, QFrame, QVBoxLayout

from views.ui_notificationframe import Ui_NotificationFrame


class NotificationFrame(QFrame):
    INFO, WARNING, ERROR = range(3)

    def __init__(self, parent, message, severity):
        QFrame.__init__(self, parent)
        self.ui = Ui_NotificationFrame()

        if severity == self.INFO:
            bgcolor = "#4398c8"
            fgcolor = self.palette().base().color().name()
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation).pixmap(36, 36)
        elif severity == self.WARNING:
            bgcolor = "#d0b05f"
            fgcolor = self.palette().text().color().name()
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(36, 36)
        elif severity == self.ERROR:
            bgcolor = "#cda8a8"
            fgcolor = self.palette().text().color().name()
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(36, 36)

        self.ui.setupUi(self)
        self.ui.iconLabel.setPixmap(icon)
        self.ui.messageLabel.setText(message)
        self._setColor(bgcolor, fgcolor)

    def _setColor(self, bgcolor, fgcolor):
        stylesheet = \
        """
        #NotificationFrame {
          border-radius: 5px;
          padding: 2px;
          background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 0.1 %s, stop: 1 %s);
          border: 1px solid %s;
        }
        #messageLabel {
          color: %s;
        }"""

        def lighter(c):
            return QColor(c).lighter(110).name()

        def darker(c):
            return QColor(c).darker(110).name()

        self.setStyleSheet(stylesheet % (lighter(bgcolor), bgcolor, darker(bgcolor), "black", fgcolor))


class NotificationFrameHandler(logging.Handler):
    def __init__(self, notificationArea):
        logging.Handler.__init__(self)
        self._notificationArea = notificationArea
        self._notificationArea.setLayout(QVBoxLayout())

    def emit(self, record):
        w = None
        if record.levelno >= logging.ERROR:
            w = NotificationFrame(self._notificationArea, record.message, NotificationFrame.ERROR)
        elif record.levelno >= logging.WARNING:
            w = NotificationFrame(self._notificationArea, record.message, NotificationFrame.WARNING)
        elif record.levelno >= logging.INFO:
            w = NotificationFrame(self._notificationArea, record.message, NotificationFrame.INFO)

        if w:
            self._notificationArea.layout().addWidget(w)
