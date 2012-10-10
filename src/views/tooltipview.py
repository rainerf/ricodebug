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

from .treeitemview import TreeItemView
from PyQt4.QtCore import Qt, QTimer, QModelIndex
from PyQt4.QtGui import QWidget, QPushButton, QIcon, QHBoxLayout, QVBoxLayout, \
        QSizeGrip, QSpacerItem, QSizePolicy, QStylePainter, QStyleOptionFrame, QStyle, QToolTip


class ToolTipView(QWidget):
    ICON_SIZE = 22

    def __init__(self, distributedObjects, parent=None):
        QWidget.__init__(self, parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setPalette(QToolTip.palette())

        self.__do = distributedObjects
        self.__allowHide = True
        self.treeItemView = TreeItemView()
        self.hide()

        self.exp = None

        self.addToWatchButton = QPushButton(QIcon(":/icons/images/watch.png"), "")
        self.addToWatchButton.setMinimumSize(self.ICON_SIZE, self.ICON_SIZE)
        self.addToWatchButton.setMaximumSize(self.ICON_SIZE, self.ICON_SIZE)
        self.addToWatchButton.setToolTip("Add to Watch")
        self.addToWatchButton.clicked.connect(self.__addToWatch)
        self.addToDatagraphButton = QPushButton(QIcon(":/icons/images/datagraph.png"), "")
        self.addToDatagraphButton.setMinimumSize(self.ICON_SIZE, self.ICON_SIZE)
        self.addToDatagraphButton.setMaximumSize(self.ICON_SIZE, self.ICON_SIZE)
        self.addToDatagraphButton.setToolTip("Add to Data Graph")
        self.addToDatagraphButton.clicked.connect(self.__addToDatagraph)

        self.__layout = QHBoxLayout(self)
        self.__layout.addWidget(self.treeItemView)
        l = QVBoxLayout()
        l.addWidget(self.addToWatchButton)
        l.addWidget(self.addToDatagraphButton)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # show a size grip in the corner to allow the user to resize the window
        l.addWidget(QSizeGrip(self))
        l.setSpacing(0)
        self.__layout.addLayout(l)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        self.__hideTimer = QTimer()
        self.__hideTimer.setSingleShot(True)
        self.__hideTimer.timeout.connect(self.hide)

        self.treeItemView.contextMenuOpen.connect(self.__setAllowHide)
        self.treeItemView.setRootIsDecorated(False)
        self.treeItemView.setHeaderHidden(True)

    def hide(self):
        if self.__allowHide:
            QWidget.hide(self)

    def __setAllowHide(self, x):
        self.__allowHide = not x

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
        self.resize(300, 90)

        # store the expression for __addToWatch and __addToDatagraph
        self.exp = exp

        # expand the item shown in the tool tip to save the user some work ;)
        self.treeItemView.setExpanded(self.treeItemView.model().index(0, 0, QModelIndex()), True)
        self.updateGeometry()

        QWidget.show(self)

    def setModel(self, model):
        self.treeItemView.setModel(model)

    def paintEvent(self, event):
        # this makes the tool tip use the system's tool tip color as its background
        painter = QStylePainter(self)
        opt = QStyleOptionFrame()
        opt.initFrom(self)
        painter.drawPrimitive(QStyle.PE_PanelTipLabel, opt)
