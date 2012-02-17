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

from PyQt4.QtGui import QToolBar, QLineEdit, QIcon
from PyQt4.QtCore import QObject


class QuickWatch(QToolBar):
    def __init__(self, parent, distributedObjects):
        QObject.__init__(self, "QuickWatch")
        self.setObjectName("QuickWatch")
        parent.addToolBar(self)
        self.watchedit = QLineEdit()
        self.watchedit.setFixedHeight(28)
        self.addWidget(self.watchedit)
        self.distributedObjects = distributedObjects
        self.addAction(QIcon(":/icons/images/watch.png"), "Add to Watch", self.addToWatch)
        self.addAction(QIcon(":/icons/images/datagraph.png"), "Add to Data Graph", self.addToDG)

    def addToWatch(self):
        self.distributedObjects.watchController.addWatch(self.watchedit.text())

    def addToDG(self):
        self.distributedObjects.datagraphController.addWatch(self.watchedit.text())
