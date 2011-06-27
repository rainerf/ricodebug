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

""" @package filelistview
A view that displays the content of the file list model.
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDockWidget, QWidget
from PyQt4.QtCore import QObject, SIGNAL

class FileListView(QWidget):
    """ Class that displays the content of the file list model in a tree view. """

    def __init__(self, filelist_controller, parent = None):
        """ The constructor.
        @param filelist_controller The file list controller.
        @param parent The parent item. 
        """

        QWidget.__init__(self, parent)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)

        self.treeView = QtGui.QTreeView(self)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        QObject.connect(self.treeView, SIGNAL('activated(QModelIndex)'), filelist_controller.fileInFileListViewActivated)
        QObject.connect(self.treeView, SIGNAL('expanded(QModelIndex)'), self.resizeColumn)
        
    def resizeColumn(self, index):
        """ Resize the first column to contents when expanded. 
        @param index The index of the column (ignored).
        """
        self.treeView.resizeColumnToContents(0)
        
