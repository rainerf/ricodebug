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

from treeitemview import TreeItemView
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QWidget, QPushButton, QIcon, QGridLayout, QSizeGrip


class ToolTipView(QWidget):
    def __init__(self, distributedObjects, parent=None):
        QWidget.__init__(self, parent)
        self.__do = distributedObjects
        self.treeItemView = TreeItemView()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.hide()
        self.resize(300, 150)

        self.exp = None

        self.addToWatchButton = QPushButton(QIcon(":/icons/images/watch.png"), "")
        self.addToDatagraphButton = QPushButton(QIcon(":/icons/images/datagraph.png"), "")
        self.addToWatchButton.clicked.connect(self.__addToWatch)
        self.addToDatagraphButton.clicked.connect(self.__addToDatagraph)

        self.__layout = QGridLayout(self)
        self.__layout.addWidget(self.addToWatchButton, 0, 0)
        self.__layout.addWidget(self.addToDatagraphButton, 0, 1)
        self.__layout.addWidget(self.treeItemView, 1, 0, 1, -1)
        self.__layout.setContentsMargins(1, 1, 1, 1)
        self.__layout.setVerticalSpacing(0)

        # show a size grip in the corner to allow the user to resize the window
        self.treeItemView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.treeItemView.setCornerWidget(QSizeGrip(self))

        self.__hideTimer = QTimer()
        self.__hideTimer.setSingleShot(True)
        self.__hideTimer.timeout.connect(self.hide)

    def enterEvent(self, event):
        self.__hideTimer.stop()

    def hideLater(self):
        self.__hideTimer.start(250)

    # hide the widget when the mouse leaves it
    def leaveEvent(self, event):
        self.hideLater()

    def __addToWatch(self):
        self.__do.signalProxy.addWatch(self.exp)

    def __addToDatagraph(self):
        self.__do.datagraphController.addWatch(self.exp)

    def show(self, exp):
        # store the expression for __addToWatch and __addToDatagraph
        self.exp = exp
        self.addToWatchButton.setText("Add '%s' to Watch" % exp)
        self.addToDatagraphButton.setText("Add '%s' to Data Graph" % exp)

        QWidget.show(self)

    def setModel(self, model):
        self.treeItemView.setModel(model)
