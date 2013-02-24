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
import importlib

from PyQt4 import QtCore

from helpers.icons import Icons
from variables.arrayvariable import ArrayVariable
from .datagraphvariables import ComplexTemplateHandler, ComplexDataGraphVariableBase
from .stdvariableview import DataGraphStdVariable

plt = None  # this will be imported lazily


def _importMatplotlib():
    if "matplotlib" not in sys.modules:
        global plt
        import matplotlib
        matplotlib.use('Agg')
        plt = importlib.import_module("matplotlib.pyplot")


def _getAvailableFilters():
    return [Bar, Lines, Steps]


def add_actions_for_all_styles(menu, handler):
    def setPlotStyle(handler, style):
        def f():
            handler.setPlotStyle(style)
        return f

    for cls in _getAvailableFilters():
        name = cls.__doc__
        menu.addAction(name, setPlotStyle(handler, cls))


class Bar:
    "Bar chart"
    @staticmethod
    def plot(ax, data):
        ind = range(len(data))
        width = 0.75

        ax.bar(ind, data, width)
        ax.set_xticks([i + width / 2 for i in ind])
        ax.set_xticklabels(ind)
        ax.set_xlim(0, len(data) - 1 + width)


class Lines:
    "Lines plot"
    @staticmethod
    def plot(ax, data):
        ax.plot(data)
        ind = range(len(data))
        ax.set_xticks(range(len(data)))
        ax.set_xticks([i for i in ind])
        ax.set_xlim(0, len(data) - 1)


class Steps:
    "Steps plot"
    @staticmethod
    def plot(ax, data):
        ax.plot(data, drawstyle='steps-post')
        ind = range(len(data))
        ax.set_xticks(range(len(data)))
        ax.set_xticks([i + 0.5 for i in ind])
        ax.set_xticklabels(ind)
        ax.set_xlim(0, len(data))


class ArrayVariableTemplateHandler(ComplexTemplateHandler):
    """ TemplateHandler for Arrays """
    def __init__(self, var):
        ComplexTemplateHandler.__init__(self, var, 'structvariableview.mako')
        self.graphicalView = False
        self.style = Bar

    @QtCore.pyqtSlot()
    def toggleGraphicalView(self):
        if self.graphicalView:
            self.graphicalView = False
            self.setTemplate('structvariableview.mako')
        else:
            self.graphicalView = True
            self.setTemplate('arrayview.mako')
        self.var.setDirty(True)

    def prepareContextMenu(self, menu):
        ComplexTemplateHandler.prepareContextMenu(self, menu)

        graphicalViewPossible = all(isinstance(var, DataGraphStdVariable) for var in self.var.childs)

        # we only allow the graphical view if all contained elements are standard variables; also,
        # do not show the menu if the variable view is collapsed
        if self.var.isOpen and graphicalViewPossible:
            action = menu.addAction(Icons.graph, "Graphical view for %s" % self.var.exp, self.toggleGraphicalView)
            action.setCheckable(True)
            action.setChecked(self.graphicalView)

            if self.graphicalView:
                submenu = menu.addMenu("Set plot type")
                add_actions_for_all_styles(submenu, self)

    def setPlotStyle(self, style):
        self.style = style
        self.var.setDirty(True)

    def plot(self, output):
        _importMatplotlib()  # only import matplotlib if we really need it
        data = [float(var._value) for var in self.var.childs]

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(111)
        self.style.plot(ax, data)
        fig.savefig(output, format='svg', transparent=True, bbox_inches='tight')


class DataGraphArrayVariable(ArrayVariable, ComplexDataGraphVariableBase):
    def __init__(self, *args):
        ArrayVariable.__init__(self, *args)
        ComplexDataGraphVariableBase.__init__(self, ArrayVariableTemplateHandler(self))

    def _loadChildrenFromGdb(self):
        ArrayVariable._loadChildrenFromGdb(self)
        self._setDataForChilds()
