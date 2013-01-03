# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2012  The ricodebug project team at the
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


from PyQt4.QtGui import QDockWidget, QAction, QIcon
from PyQt4.QtCore import pyqtSignal
from .docktitlebar import DockTitleBar
from helpers.icons import Icons


class AlertableDockWidget(QDockWidget):
    windowIconChanged = pyqtSignal(QIcon)
    windowTitleChanged = pyqtSignal(str)
    alerted = pyqtSignal(bool)
    clearRequested = pyqtSignal()

    def __init__(self, name, parent):
        QDockWidget.__init__(self, name, parent)
        self.titleBar = DockTitleBar(self)
        self.setTitleBarWidget(self.titleBar)

        # we do not know the initial state yet but will get an event on
        # visibilityChanged as soon as the windows are first shown
        self.__visible = None
        self.visibilityChanged.connect(self.__updateVisibility)

    visible = property(lambda self: self.__visible)

    def addClearAction(self):
        self.addAction(QAction(Icons.clear, "Clear", self)).triggered.connect(lambda: self.clearRequested.emit())

    def addAction(self, action):
        return self.titleBarWidget().addAction(action)

    def setAlerted(self):
        if self.__visible:
            return
        self.alerted.emit(True)

    def __updateVisibility(self, visible):
        self.__visible = visible
        if self.__visible:
            self.setNormal()

    def setNormal(self):
        self.alerted.emit(False)

    def setWindowIcon(self, icon):
        QDockWidget.setWindowIcon(self, icon)
        self.windowIconChanged.emit(icon)

    def setWindowTitle(self, text):
        QDockWidget.setWindowTitle(self, text)
        self.windowTitleChanged.emit(text)
