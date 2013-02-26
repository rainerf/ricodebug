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

import sys

from mako.template import Template
from mako.lookup import TemplateLookup
from PyQt4.QtCore import QObject
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidgetAction, QLabel, QIcon

from .htmlvariableview import HtmlVariableView


class Role:
    NORMAL, INCLUDE_HEADER, VALUE_ONLY = range(3)


class HtmlTemplateHandler(QObject):
    """ Parent of all TemplateHandler-Classes. <br>
    renders the htmlTemplate
    """

    def __init__(self, var, template):
        QObject.__init__(self)
        self.var = var
        self.id = None  # our unique id which we can use inside the rendered HTML/JS

        self._templateLookup = TemplateLookup(directories=[sys.path[0] + "/datagraph/templates/"])

        self._htmlTemplate = None
        self.setTemplate(template)

    def setTemplate(self, template):
        self._htmlTemplate = Template(filename=sys.path[0] + "/datagraph/templates/" + template, lookup=self._templateLookup)

    def render(self, role, **kwargs):
        """ renders the html-Template and saves and returns the rendered html-Code
        @return rendered html-Code
        """
        assert self._htmlTemplate is not None
        assert self.var.getView()

        if not self.id:
            self.id = self.var.getView().getUniqueId(self)

        return self._htmlTemplate.render(var=self.var, role=role, id=self.id, **kwargs)

    @QtCore.pyqtSlot()
    def openContextMenu(self):
        self.var.openContextMenu()

    @QtCore.pyqtSlot(str)
    def setValue(self, value):
        self.var.assignValue(value)

    def prepareContextMenu(self, menu):
        menu.addSeparator()
        self.addContextMenuLabel(menu)

    # insert a "header" into the menu for the current element
    def addContextMenuLabel(self, menu):
        label = QLabel("Actions for %s" % self.var.exp)
        label.setStyleSheet("color:palette(light); background-color:palette(dark); margin-top:2px; margin-bottom:2px; margin-left:2px; margin-right:2px;")
        we = QWidgetAction(menu)
        we.setDefaultWidget(label)
        menu.addAction(we)

    @QtCore.pyqtSlot()
    def remove(self):
        self.die()


class ComplexTemplateHandler(HtmlTemplateHandler):
    def __init__(self, var, template):
        HtmlTemplateHandler.__init__(self, var, template)
        self.vertical = True

    @QtCore.pyqtSlot()
    def toggleCollapsed(self):
        self.var.setOpen(not self.var.isOpen)

    @QtCore.pyqtSlot()
    def toggleVertical(self):
        self.vertical = not self.vertical

        # the way our children will be rendered will change too (include/skip
        # <tr> etc), so mark them as dirty, but do not force immediate rerendering;
        # this will be done when we mark ourselves as dirty
        for child in self.var.getChildren():
            child.setDirty(False)
        self.var.setDirty(True)

    def prepareContextMenu(self, menu):
        HtmlTemplateHandler.prepareContextMenu(self, menu)

        action = menu.addAction(QIcon(":/icons/images/collapse.png"), "Collapse %s" % self.var.exp, self.toggleCollapsed)
        action.setCheckable(True)
        action.setChecked(not self.var.isOpen)

        if self.var.isOpen:
            action = menu.addAction(QIcon(":/icons/images/vertical.png"), "Vertical view for %s" % self.var.exp, self.toggleVertical)
            action.setCheckable(True)
            action.setChecked(self.vertical)

    def render(self, role, **kwargs):
        return HtmlTemplateHandler.render(self, role, vertical=self.vertical, **kwargs)


class DataGraphVariableBase:
    def __init__(self, templateHandler):
        self._view = None
        self.templateHandler = templateHandler
        self.parent = None
        self.dirty = True  # true if we need to rerender our stuff
        self.changed.connect(lambda: self.setDirty(True))
        self.source = ""
        self.do = None

    def createView(self):
        self._view = HtmlVariableView(self)
        self.parent = self._view

    def setExistingView(self, view, parent):
        self._view = view
        self.parent = parent

    def getView(self):
        return self._view

    def openContextMenu(self, menu=None):
        if not menu:
            menu = QtGui.QMenu()
        self.templateHandler.prepareContextMenu(menu)
        self.parent.openContextMenu(menu)

    def changeTemplateHandler(self, type_):
        self.templateHandler = type_(self, self.distributedObjects)
        self.setDirty(True)

    @QtCore.pyqtSlot()
    def setDirty(self, render_immediately=False):
        self.dirty = True
        if self.parent:
            self.parent.setDirty(render_immediately)

    def setXPos(self, xPos):
        self.getView().setX(xPos)

    def setYPos(self, yPos):
        self.getView().setY(yPos)

    def render(self, role, **kwargs):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        if self.dirty:
            self.dirty = False
            self.source = self.templateHandler.render(role, **kwargs)
        return self.source

    def setFilter(self, f):
        Variable.setFilter(self, f)
        self.setDirty(True)

    def setData(self, do):
        self.do = do


class ComplexDataGraphVariableBase(DataGraphVariableBase):
    def __init__(self, templateHandler):
        DataGraphVariableBase.__init__(self, templateHandler)
        self.isOpen = True

    def setOpen(self, open_):
        self.isOpen = open_
        self.setDirty(True)

    def getChildren(self):
        return self.childs

    def _setDataForChilds(self):
        for c in self.childs:
            c.setExistingView(self.getView(), self)
            c.setData(self.do)
