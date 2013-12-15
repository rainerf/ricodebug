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

from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QPushButton, QHBoxLayout, QVBoxLayout, QSizeGrip, QSpacerItem, QSizePolicy, QAbstractItemView

from .treeitemview import TreeItemView
from helpers.icons import Icons
from widgets.complextooltip import ComplexToolTip


class VariableViewToolTip(ComplexToolTip):
    ICON_SIZE = 22

    def __init__(self, distributedObjects, parent=None):
        ComplexToolTip.__init__(self, parent)

        self.__do = distributedObjects
        self.treeItemView = TreeItemView()
        self.treeItemView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.treeItemView.verticalScrollBar().rangeChanged.connect(self.resizeViewVertically)

        self.exp = None

        addToWatchButton = QPushButton(Icons.watch, "")
        addToWatchButton.setMinimumSize(self.ICON_SIZE, self.ICON_SIZE)
        addToWatchButton.setMaximumSize(self.ICON_SIZE, self.ICON_SIZE)
        addToWatchButton.setToolTip("Add to Watch")
        addToWatchButton.clicked.connect(self.__addToWatch)
        addToDatagraphButton = QPushButton(Icons.datagraph, "")
        addToDatagraphButton.setMinimumSize(self.ICON_SIZE, self.ICON_SIZE)
        addToDatagraphButton.setMaximumSize(self.ICON_SIZE, self.ICON_SIZE)
        addToDatagraphButton.setToolTip("Add to Data Graph")
        addToDatagraphButton.clicked.connect(self.__addToDatagraph)
        setWatchpointButton = QPushButton(Icons.wp, "")
        setWatchpointButton.setMinimumSize(self.ICON_SIZE, self.ICON_SIZE)
        setWatchpointButton.setMaximumSize(self.ICON_SIZE, self.ICON_SIZE)
        setWatchpointButton.setToolTip("Set Watchpoint")
        setWatchpointButton.clicked.connect(self.__setWatchpoint)

        self.__layout = QHBoxLayout(self)
        self.__layout.addWidget(self.treeItemView)
        l = QVBoxLayout()
        l.addWidget(addToWatchButton)
        l.addWidget(addToDatagraphButton)
        l.addWidget(setWatchpointButton)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # show a size grip in the corner to allow the user to resize the window
        l.addWidget(QSizeGrip(self))
        l.setSpacing(0)
        self.__layout.addLayout(l)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        self.treeItemView.contextMenuOpen.connect(self.setDisallowHide)
        self.treeItemView.setRootIsDecorated(False)
        self.treeItemView.setHeaderHidden(True)

        self.hidden.connect(self.onHidden)

    def onHidden(self):
        self.treeItemView.model().clear()

    def __addToWatch(self):
        self.__do.signalProxy.addWatch(self.exp)

    def __addToDatagraph(self):
        self.__do.datagraphController.addWatch(self.exp)

    def __setWatchpoint(self):
        self.__do.breakpointModel.insertWatchpoint(self.exp)

    def setExp(self, exp):
        # store the expression for __addToWatch and __addToDatagraph
        self.exp = exp

    def show(self):
        self.resize(400, 90)

        # expand the item shown in the tool tip to save the user some work ;)
        self.treeItemView.setExpanded(self.treeItemView.model().index(0, 0, QModelIndex()), True)
        self.updateGeometry()

        ComplexToolTip.show(self)

    def setModel(self, model):
        self.treeItemView.setModel(model)

    def resizeViewVertically(self, _, max_):
        itemHeight = self.treeItemView.indexRowSizeHint(self.treeItemView.model().index(0, 0, QModelIndex()))
        self.resize(self.width(), self.height() + max_ * itemHeight)
        self.treeItemView.verticalScrollBar().setRange(0, 0)
