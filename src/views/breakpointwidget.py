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

from PyQt4.QtGui import QDataWidgetMapper
from .ui_breakpointwidget import Ui_BreakpointWidget
from widgets.complextooltip import ComplexToolTip


class BreakpointWidget(ComplexToolTip):
    def __init__(self, model, bp, parent):
        ComplexToolTip.__init__(self, parent)
        self.ui = Ui_BreakpointWidget()
        self.ui.setupUi(self)

        self.ui.description.setText("Breakpoint %s at %s (%s)" % (bp.number, bp.where, bp.addr))
        self.ui.icon.setPixmap(bp.icon.pixmap(16, 16))

        row, _ = model.findRowForNumber(bp.number)
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui.enabled, 1)
        self.mapper.addMapping(self.ui.condition, 4)
        self.mapper.addMapping(self.ui.skip, 5)
        self.mapper.addMapping(self.ui.hits, 6)
        self.mapper.addMapping(self.ui.autoContinue, 7)
        self.mapper.addMapping(self.ui.name, 8)
        self.mapper.addMapping(self.ui.action, 9)
        self.mapper.setCurrentIndex(row)

        # for some reason, the enabled checkbox does not autosubmit while the autoContinue one does
        self.ui.enabled.clicked.connect(self.mapper.submit)
        #self.ui.autoContinue.clicked.connect(self.mapper.submit)
