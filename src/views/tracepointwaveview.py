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

from PyQt4.QtCore import Qt
from PyQt4 import QtGui


class TracepointWaveView(QtGui.QTableView):
    ''' TableView for TracepointWaveModel '''
    def __init__(self):
        QtGui.QTableView.__init__(self)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setMinimumSectionSize(30)
        self.verticalHeader().setDefaultSectionSize(30)
        self.setShowGrid(False)
        self.widget = QtGui.QWidget()
        self.iconlayout = QtGui.QHBoxLayout()
        self.iconlayout.setAlignment(Qt.AlignLeft)
        self.zoomInButton = QtGui.QPushButton(QtGui.QIcon(":/icons/images/zoom-in.png"), "")
        self.zoomInButton.setToolTip("Zoom in")
        self.zoomOutButton = QtGui.QPushButton(QtGui.QIcon(":/icons/images/zoom-out.png"), "")
        self.zoomOutButton.setToolTip("Zoom out")
        self.iconlayout.addWidget(self.zoomInButton)
        self.iconlayout.addWidget(self.zoomOutButton)
        self.layout = QtGui.QVBoxLayout()
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setAutoScroll(True)
        self.layout.addWidget(self)
        self.layout.addItem(self.iconlayout)
        self.widget.setLayout(self.layout)

    def getZoomInButton(self):
        return self.zoomInButton

    def getZoomOutButton(self):
        return self.zoomOutButton
