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

from .datagraphvariables import HtmlTemplateHandler, ComplexDataGraphVariableBase
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtGui import QWidgetAction, QLineEdit
from variables.ptrvariable import PtrVariable


class PtrVariableTemplateHandler(HtmlTemplateHandler):
    """ TemplateHandler for Pointer-Variables """

    def __init__(self, var):
        HtmlTemplateHandler.__init__(self, var, 'ptrvariableview.mako')

    @pyqtSlot()
    def dereference(self):
        self.var.dereference()

    @pyqtSlot()
    def showCustom(self):
        name = self.showCustomEdit.text()
        self.showCustomEdit.parent().hide()
        self.var.dereference(name)

    def prepareContextMenu(self, menu):
        HtmlTemplateHandler.prepareContextMenu(self, menu)
        menu.addAction("Dereference %s" % self.var.exp, self.dereference)
        submenu = menu.addMenu("Show custom...")

        # we cannot construct the lineedit in our ctor since it will be automatically deleted once the menu is closed
        self.showCustomEdit = QLineEdit()
        self.showCustomEdit.returnPressed.connect(self.showCustom)
        self.showCustomEdit.setText("*(%s)" % self.var.exp)
        we = QWidgetAction(menu)
        we.setDefaultWidget(self.showCustomEdit)
        submenu.addAction(we)


class DataGraphPtrVariable(PtrVariable, ComplexDataGraphVariableBase):
    pointerDereferenceRequested = pyqtSignal('PyQt_PyObject', str)

    def __init__(self, *args):
        PtrVariable.__init__(self, *args)
        ComplexDataGraphVariableBase.__init__(self, PtrVariableTemplateHandler(self))

    def _loadChildrenFromGdb(self):
        raise AttributeError("Use dereference instead.")

    def dereference(self, name=None):
        if self._pointerValid():
            if name is not None:
                self.pointerDereferenceRequested.emit(self, name)
            else:
                self.pointerDereferenceRequested.emit(self, self._childFormat % {"parent": self.uniqueName})

    def setData(self, do):
        ComplexDataGraphVariableBase.setData(self, do)
        self.pointerDereferenceRequested.connect(self.do.datagraphController.addDereferencedPointer)
