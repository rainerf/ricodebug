# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphes and SystemC features.
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

from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from QTermWidget import QTermWidget


class TermWidgetPlugin():
    # =================================
    # functions called by pluginloader
    # =================================
    def __init__(self):
        self.shellWidget = None
        self.term = None

    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""

        self.signalproxy = signalproxy

        # create and place DockWidget in mainwindow using signalproxy
        self.widget = QtGui.QDockWidget(None)
        self.widget.setObjectName("QTermWidget")
        self.widget.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Shell", None, QtGui.QApplication.UnicodeUTF8))
        self.signalproxy.addDockWidget(Qt.BottomDockWidgetArea, self.widget)

        self.term = QTermWidget()
        self.signalproxy.insertDockWidget(self, self.term, "Terminal", Qt.BottomDockWidgetArea, True)

        self.widget.visibilityChanged.connect(self.initQTermWidget)

        # FIXME: connect self.term.finished somewhere meaningful

    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.signalproxy.removeDockWidget(self)
