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
from PyQt4.QtGui import QTableView, QLabel, QTextEdit, QWidget, QGridLayout, QProgressBar
from PyQt4.QtGui import QApplication, QStyle, QFrame, QPalette, QBrush, QPushButton, QPixmap, QIcon
from PyQt4.QtCore import Qt, pyqtSlot, QTimer
from models.logmodel import LogModel, FilteredLogModel


class LogViewHandler(logging.Handler):
    def __init__(self, target_widget, filter_slider):
        logging.Handler.__init__(self)
        self.target_widget = target_widget
        self.model = LogModel()
        self.filter_model = FilteredLogModel()
        self.filter_model.setSourceModel(self.model)
        target_widget.setModel(self.filter_model)
        self.target_widget = target_widget
        filter_slider.valueChanged.connect(self.setFilter)

    def emit(self, record):
        self.model.insertMessage(record)
        self.updateView()

    def updateView(self):
        self.target_widget.resizeColumnsToContents()
        if self.target_widget.columnWidth(2) > 500:
            self.target_widget.setColumnWidth(2, 500)
        self.target_widget.scrollToBottom()

    def setFilter(self, value):
        self.filter_model.setMinimum(value * 10)
        self.updateView()


class ErrorLabel(QWidget):
    WARNING, ERROR = range(2)

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.ticks = 5
        self.elapsedTicks = 0
        self.lastSeverity = None
        self.icon_label = QLabel()
        self.icon_label.setGeometry(0, 0, 48, 48)
        self.message_edit = QTextEdit()
        self.message_edit.setReadOnly(True)
        self.message_edit.setFrameStyle(QFrame.NoFrame)
        palette = self.message_edit.palette()
        palette.setBrush(QPalette.Base, QBrush())
        self.message_edit.setPalette(palette)
        self.time_bar = QProgressBar()
        self.time_bar.setOrientation(Qt.Vertical)
        self.time_bar.setMaximum(self.ticks)
        self.time_bar.setTextVisible(False)
        self.pauseButton = QPushButton(QIcon(QPixmap(":/icons/images/pause.png")), "")
        self.pauseButton.setFixedSize(32, 32)
        self.pauseButton.clicked.connect(self.stopTimer)
        self.stopButton = QPushButton(QIcon(QPixmap(":/icons/images/stop.png")), "")
        self.stopButton.setFixedSize(32, 32)
        self.stopButton.clicked.connect(self.closeWidget)
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.time_bar, 0, 0, 2, 1)
        self.layout.addWidget(self.icon_label, 0, 1, 2, 1)
        self.layout.addWidget(self.message_edit, 0, 2, 2, 1)
        self.layout.addWidget(self.pauseButton, 0, 3)
        self.layout.addWidget(self.stopButton, 1, 3)
        self.layout.setColumnStretch(2, 1)
        self.setAutoFillBackground(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.decrementTime)

    def stopTimer(self):
        self.timer.stop()
        self.pauseButton.setEnabled(False)

    def closeWidget(self):
        self.timer.stop()
        QWidget.hide(self)

    @pyqtSlot()
    def decrementTime(self):
        if self.elapsedTicks == self.ticks:
            self.hide()
            self.timer.stop()
        else:
            self.elapsedTicks += 1
            self.time_bar.setValue(self.ticks - self.elapsedTicks)

    def updatePosition(self):
        self.setGeometry(0, self.parent().height() - self.height(), self.width(), self.height())

    def setSize(self, w, h):
        self.setGeometry(0, self.parent().height() - h, w, h)

    def setErrorMessage(self, msg):
        self.lastSeverity = self.ERROR
        self.icon_label.setPixmap(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(48, 48))
        self._setMessage(msg)

    def setWarningMessage(self, msg):
        self.lastSeverity = self.WARNING
        self.icon_label.setPixmap(QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(48, 48))
        self._setMessage(msg)

    def _setMessage(self, msg):
        self.message_edit.setText(msg)
        self.updatePosition()
        self.elapsedTicks = 0
        self.time_bar.setValue(self.ticks)
        self.timer.start(1000)
        self.pauseButton.setEnabled(True)
        self.show()


class ErrorLabelHandler(logging.Handler):
    def __init__(self, main_window):
        logging.Handler.__init__(self)
        self.main_window = main_window

        self.error_label = ErrorLabel(main_window)
        self.error_label.setSize(500, 100)
        self.error_label.hide()

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.error_label.setErrorMessage("<b>%s</b>" % record.message)
        elif record.levelno >= logging.WARNING:
            self.error_label.setWarningMessage("<b>%s</b>" % record.message)


class LogView(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

