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

""" @package filelistmodel
A tree model that provides data for the file list view.
"""

import os
from operator import attrgetter
from PyQt4.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject, SIGNAL
from PyQt4.QtGui import QPixmap

class FileListItem():
    """ Class that represents a source file in the file list view. """

    def __init__(self, data, imageIndex, parent = None):
        """ The constructor.
        @param data The item's data.
        @param imageIndex The index of the item's icon.
        @param parent The parent item.
        """

        self.childItems = []
        self.itemData = data
        self.parentItem = parent
        self.imageIndex = imageIndex
        
    def appendChild(self, child):
        """ Append child to current item. 
        @param child Child object.
        """
        self.childItems.append(child)
        
    def clearChildren(self):
        """ Clear children of current item. """
        self.childItems = []

    def child(self, row):
        """ Get child.
        @param row Row index of the child.
        """
        return self.childItems[row]
    
    def childCount(self):
        """ Get number of children. """
        return len(self.childItems)
    
    def columnCount(self):
        """ Get number of data columns. """
        return len(self.itemData)
    
    def data(self, column):
        """ Get data. 
        @param column The data column. 
        """
        return self.itemData[column]
    
    def row(self):
        """ Get row index. """
        if self.parentItem is None:
            return self.parentItem.childItems.index(self);
        
        return 0;
    
    def parent(self):
        """ Get parent. """
        return self.parentItem

class FileListModel(QAbstractItemModel):
    """ Class that represents a tree model for the program's source files. """

    def __init__(self, debugger, connector, parent = None):
        """ The constructor.
        @param debugger The debug controller.
        @param connector The GDB connector.
        @param parent The parent item.
        """
 
        QAbstractItemModel.__init__(self, parent)
        self.connector = connector
        self.debug_controller = debugger
        self.imgs = [QPixmap(":/icons/images/folder.png"), QPixmap(":/icons/images/file.png")]
        self.root = FileListItem(["Name", "Path"], 0)
        self.sources = FileListItem(["Sources", ""], 0, self.root)
        self.headers = FileListItem(["Headers", ""], 0, self.root)
        self.others = FileListItem(["Others", ""], 0, self.root)
        
        QObject.connect(self.debug_controller, SIGNAL('executableOpened'), self.update)
       
    def data(self, index, role):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if not index.isValid():
            return None
        
        item = index.internalPointer()
        
        ret = None
        if role == Qt.DisplayRole:
            ret = item.data(index.column())
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                ret = self.imgs[item.imageIndex]
            
        return ret

    def flags(self, index):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if not index.isValid():
            return 0;

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root.data(section)

        return None

    def index(self, row, column, parent):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if not self.hasIndex(row, column, parent):
            return QModelIndex();
        
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()
            
        childItem = parentItem.child(row)
        if childItem is not None:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if not index.isValid():
            return QModelIndex()
        
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        
        if parentItem == self.root:
            return QModelIndex()
        
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()
            
        return parentItem.childCount();
    
    def columnCount(self, parent):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.root.columnCount();
        
    def updateData(self):
        """ Builds the tree model. """

        data = self.connector.getSources()
        self.clearData()
        
        for path in data:
            name = os.path.basename(path)
            file, ext = os.path.splitext(name)
            if ext == ".cpp" or ext == ".c":
                if not self.sources in self.root.childItems: 
                    self.root.appendChild(self.sources)
                item = FileListItem([name, path], 1, self.sources)
                self.sources.appendChild(item)
            elif ext == ".hpp" or ext == ".h":
                if not self.headers in self.root.childItems: 
                    self.root.appendChild(self.headers)
                item = FileListItem([name, path], 1, self.headers)
                self.headers.appendChild(item)
            else:
                if not self.others in self.root.childItems: 
                    self.root.appendChild(self.others)
                item = FileListItem([name, path], 1, self.others)
                self.others.appendChild(item)
                
        self.sources.childItems.sort(key=attrgetter("itemData"), reverse=False)
        self.headers.childItems.sort(key=attrgetter("itemData"), reverse=False)
        self.others.childItems.sort(key=attrgetter("itemData"), reverse=False)
       
    def clearData(self):
        """ Clears all data in the tree model. """

        self.root.clearChildren()
        self.sources.clearChildren()
        self.headers.clearChildren()
        self.others.clearChildren()

    def clear(self):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        self.beginResetModel()
        self.clearData()
        self.endResetModel()

    def update(self):
        """ Required function for Qt Model/View concepts.
        Please see Qt documentation for further information.
        """

        self.beginResetModel()
        self.updateData()
        self.endResetModel()
        
