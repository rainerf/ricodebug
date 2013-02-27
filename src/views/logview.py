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

import logging
from PyQt4.QtGui import QWidget
from models.logmodel import LogModel, FilteredLogModel
from views.ui_logviewtab import Ui_LogViewTab


class LogViewHandler(logging.Handler, QWidget):
    def __init__(self, parent):
        logging.Handler.__init__(self)
        QWidget.__init__(self, parent)

        self.ui = Ui_LogViewTab()
        self.ui.setupUi(self)
        self.model = LogModel()
        self.filter_model = FilteredLogModel()
        self.filter_model.setSourceModel(self.model)
        self.ui.logView.setModel(self.filter_model)
        self.ui.filterSlider.valueChanged.connect(self.setFilter)
        self.ui.filterSlider.setValue(3)

        self.parent().addClearAction()
        self.parent().clearRequested.connect(self.model.clear)

    def emit(self, record):
        self.model.insertMessage(record)
        self.updateView()

    def updateView(self):
        self.ui.logView.resizeColumnsToContents()
        if self.ui.logView.columnWidth(2) > 500:
            self.ui.logView.setColumnWidth(2, 500)
        self.ui.logView.scrollToBottom()

    def setFilter(self, value):
        self.filter_model.setMinimum(value * 10)
        self.updateView()
