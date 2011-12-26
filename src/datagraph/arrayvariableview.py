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

from datagraph.datagraphvw import ComplexDataGraphVW, ComplexTemplateHandler
from stdvariableview import StdDataGraphVW
from PyQt4 import QtCore
import matplotlib
matplotlib.use('Agg')

class ArrayVariableTemplateHandler(ComplexTemplateHandler):
    """ TemplateHandler for Arrays """
    
    def __init__(self, varWrapper, distributedObjects):
        """ Constructor
        @param varWrapper    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        ComplexTemplateHandler.__init__(self, varWrapper, distributedObjects, 'structvariableview.mako')
        self.graphicalView = False
    
    @QtCore.pyqtSlot()
    def setStdView(self):
        self.graphicalView = False
        self.setTemplate('structvariableview.mako')
        self.varWrapper.setDirty(True)
    
    @QtCore.pyqtSlot()
    def setGraphicalView(self):
        self.graphicalView = True
        self.setTemplate('arrayview.mako')
        self.varWrapper.setDirty(True)
    
    def render(self, top, **kwargs):
        if self.graphicalView:
            data = [var.getValue() for var in self.varWrapper.children]
            return ComplexTemplateHandler.render(self, top, data=data)
        else:
            return ComplexTemplateHandler.render(self, top)
    
    def prepareContextMenu(self, menu):
        ComplexTemplateHandler.prepareContextMenu(self, menu)
        if self.graphicalView:
            menu.addAction("Change to standard view for %s" % self.varWrapper.getExp(), self.setStdView)
        else:
            # we only allow the graphical view if all contained elements are standard variables
            graphicalViewPossible = all(isinstance(var, StdDataGraphVW) for var in self.varWrapper.children)
            
            if graphicalViewPossible:
                menu.addAction("Change to graphical view for %s" % self.varWrapper.getExp(), self.setGraphicalView)


class ArrayDataGraphVW(ComplexDataGraphVW):
    """ VariableWrapper for Arrays """
    
    def __init__(self, variable, distributedObjects, vwFactory):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        ComplexDataGraphVW.__init__(self, variable, distributedObjects, vwFactory, ArrayVariableTemplateHandler(self, distributedObjects))
