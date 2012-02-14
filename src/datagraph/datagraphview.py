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

from PyQt4.QtCore import Qt, pyqtSlot
from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QMenu, QIcon
import logging
import pointer
import htmlvariableview


class DataGraphView(QGraphicsView):
    """ the View that shows the DataGraph <br>
        holds all VariableViews (datagraph.htmlvariableview.HtmlVariableView) on its scene (QGraphicsScene)
    """
    def __init__(self, parent, datagraphcontroller):
        """    Constructor
        @param parent                parent for the QGraphicsView-Constructor, can be None
        @param datagraphcontroller    datagraph.datagraphcontroller.DataGraphController, Reference to the DataGraphController
        """
        QGraphicsView.__init__(self, parent)
        self.setScene(QGraphicsScene())
        self.topLevelItems = []
        self.leafItems = {}
        self.model = None
        self.data_graph_controller = datagraphcontroller
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def clear(self):
        """ deletes all VariableViews from the DataGraph """
        self.scene().clear()

    def addItem(self, var):
        """    adds var to the DataGraphView
        @param var    datagraph.htmlvariableview.HtmlVariableView, VariableView to add """
        self.scene().addItem(var)

    def removeItem(self, var):
        """    removes var from the DataGraphView
        @param var    datagraph.htmlvariableview.HtmlVariableView, VariableView to remove
        """
        if var in self.scene().items():
            self.scene().removeItem(var)

    @pyqtSlot()
    def zoomIn(self):
        self.scale(1.2, 1.2)

    @pyqtSlot()
    def zoomOut(self):
        self.scale(1 / 1.2, 1 / 1.2)

    @pyqtSlot()
    def zoomToFit(self):
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

    @pyqtSlot()
    def zoomInitial(self):
        self.resetTransform()

    def contextMenuEvent(self, event):
        QGraphicsView.contextMenuEvent(self, event)

        # if some item was under the mouse and showed its context menu, the event will
        # have been accepted
        if not event.isAccepted():
            menu = QMenu()
            menu.addAction(QIcon(":/icons/images/viewmag+.png"), "Zoom in", self.zoomIn)
            menu.addAction(QIcon(":/icons/images/viewmag-.png"), "Zoom out", self.zoomOut)
            menu.addAction(QIcon(":/icons/images/viewmagfit.png"), "Zoom to fit", self.zoomToFit)
            menu.addAction(QIcon(":/icons/images/viewmag1.png"), "Zoom 1:1", self.zoomInitial)
            menu.addAction("Layout", self.layout)
            menu.exec_(event.globalPos())

    def wheelEvent(self, event):
        if event.orientation() == Qt.Vertical:
            if event.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()

    @pyqtSlot()
    def layout(self):
        try:
            import pydot
        except:
            logging.error("pydot not found, cannot layout!")
            return

        index = 0
        items = []
        nodes = {}

        g = pydot.Dot(graph_type="digraph")
        #g.set_rankdir('LR')
        for i in self.scene().items():
            if isinstance(i, htmlvariableview.HtmlVariableView):
                n = pydot.Node(str(index))
                items.append(i)
                index = index + 1
                nodes[i] = n

                g.add_node(n)
                n.set_fixedsize('true')
                n.set_shape('box')
                br = i.boundingRect()
                n.set_width(str(float(br.width()) / 72))
                n.set_height(str(float(br.height()) / 72))

        for i in self.scene().items():
            if isinstance(i, pointer.Pointer):
                g.add_edge(pydot.Edge(nodes[i.fromView], nodes[i.toView]))

        g_with_pos = pydot.graph_from_dot_data(g.create_dot())
        for n in g_with_pos.get_nodes():
            pos = n.get_pos()
            if pos:
                x, y = pos.strip('"').split(",")
                x, y = float(x), float(y)
                index = int(n.get_name())
                items[index].setX(x)
                items[index].setY(y)
