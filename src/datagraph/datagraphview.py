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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QGraphicsView, QGraphicsScene

class DataGraphView(QGraphicsView):
	""" the View that shows the DataGraph <br>
		holds all VariableViews (datagraph.htmlvariableview.HtmlVariableView) on its scene (QGraphicsScene)
	"""
	def __init__(self, parent, datagraphcontroller):
		"""	Constructor
		@param parent				parent for the QGraphicsView-Constructor, can be None
		@param datagraphcontroller	datagraph.datagraphcontroller.DataGraphController, Reference to the DataGraphController
		"""
		QGraphicsView.__init__(self, parent)
		self.setScene(QGraphicsScene())
		self.topLevelItems = []
		self.leafItems = {}
		self.model = None
		self.data_graph_controller = datagraphcontroller
	
	def clear(self):
		""" deletes all VariableViews from the DataGraph """
		self.scene().clear()
	
	def addItem(self, var):
		"""	adds var to the DataGraphView
		@param var	datagraph.htmlvariableview.HtmlVariableView, VariableView to add """
		self.scene().addItem(var)
	
	def removeItem(self, var):
		"""	removes var from the DataGraphView
		@param var	datagraph.htmlvariableview.HtmlVariableView, VariableView to remove
		"""
		if var in self.scene().items():
			self.scene().removeItem(var)
	
	def zoomIn(self):
		self.scale(1.2, 1.2)

	def zoomOut(self):
		self.scale(1/1.2, 1/1.2)
	
	def wheelEvent(self, event):
		if event.orientation() == Qt.Vertical:
			if event.delta() > 0:
				self.zoomIn()
			else:
				self.zoomOut()
