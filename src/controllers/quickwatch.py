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

from PyQt4.QtGui import QToolBar, QComboBox, QSizePolicy
from helpers.configstore import ConfigSet, SelectionConfigItem
from helpers.icons import Icons


class QuickWatchConfig(ConfigSet):
    def __init__(self):
        ConfigSet.__init__(self, "Quick Watch", "Quick Watch Settings", Icons.watch)
        self.addTo = SelectionConfigItem(self, "Enter adds element to...", "nothing", ["nothing", "Watch View", "Data Graph View"])


class QuickWatch(QToolBar):
    def __init__(self, parent, distributedObjects):
        QToolBar.__init__(self, "QuickWatch")
        self.config = QuickWatchConfig()
        distributedObjects.configStore.registerConfigSet(self.config)

        self.setObjectName("QuickWatch")
        parent.addToolBar(self)
        self.watchedit = QComboBox()
        self.watchedit.setFixedHeight(28)
        self.watchedit.setInsertPolicy(QComboBox.NoInsert)
        self.watchedit.setEditable(True)
        self.watchedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.addWidget(self.watchedit)
        self.distributedObjects = distributedObjects
        self.addAction(Icons.watch, "Add to Watch", self.addToWatch)
        self.addAction(Icons.datagraph, "Add to Data Graph", self.addToDG)
        self.watchedit.lineEdit().returnPressed.connect(self.returnPressed)

    def __addCurrentText(self):
        text = self.watchedit.lineEdit().text()
        idx = self.watchedit.findText(text)
        if idx == -1:
            self.watchedit.addItem(text)
        self.watchedit.setEditText("")

    def returnPressed(self):
        if self.config.addTo.value == "Watch View":
            self.addToWatch()
        elif self.config.addTo.value == "Data Graph View":
            self.addToDG()

    def addToWatch(self):
        self.distributedObjects.watchModel.addVar(self.watchedit.lineEdit().text())
        self.__addCurrentText()

    def addToDG(self):
        self.distributedObjects.datagraphController.addWatch(self.watchedit.lineEdit().text())
        self.__addCurrentText()
