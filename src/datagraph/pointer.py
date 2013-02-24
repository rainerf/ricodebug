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

import math
import logging

from PyQt4.QtGui import QColor, QPolygonF, QBrush, QPen, QGraphicsLineItem, QPainter
from PyQt4.QtCore import QPointF, QLineF, QRectF, QSizeF


class Pointer(QGraphicsLineItem):
    """ QGraphicsPolygonItem to model a Pointer as an Arrow from a Pointer-Variable to its Content. """
    fgcolor = QColor(0, 0, 0)
    bgcolor = QColor(0, 0, 0)

    def __init__(self, parent, fromView, toView, distributedObjects):
        """ Constructor
        @param parent                parent for the QGraphicsPolygonItem-Constructor
        @param fromView              datagraph.htmlvariableview.HtmlVariableView, starting point of the Pointer
        @param toView                datagraph.htmlvariableview.HtmlVariableView, end point of the Pointer
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        fromView and toView are QGraphicsWebViews
        """
        QGraphicsLineItem.__init__(self, parent)
        self.fromView = fromView
        fromView.addOutgoingPointer(self)
        self.toView = toView
        toView.addIncomingPointer(self)
        self.setPen(QPen(self.fgcolor, 1))

        self.distributedObjects = distributedObjects

        self.fromView.geometryChanged.connect(self.updatePosition)
        self.toView.geometryChanged.connect(self.updatePosition)
        self.fromView.xChanged.connect(self.updatePosition)
        self.fromView.yChanged.connect(self.updatePosition)
        self.toView.xChanged.connect(self.updatePosition)
        self.toView.yChanged.connect(self.updatePosition)
        self.fromView.removing.connect(self.delete)
        self.toView.removing.connect(self.delete)

        self.arrowhead = QPolygonF()
        self.arrowSize = 20
        self.setZValue(-1)  # paint the arrows behind (lower z-value) everything else

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2
        return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(),
                                               self.line().p2().y() - self.line().p1().y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowhead)
        return path

    def updatePosition(self):
        line = QLineF(self.mapFromItem(self.fromView, 0, 0), self.mapFromItem(self.toView, 0, 0))
        self.setLine(line)

    def paint(self, painter, _1, _2):
        """ Main-Method of the Pointer-Class <br>
            calculates/renders/draws the Lines of the Arrow
        """
        if self.fromView.collidesWithItem(self.toView):
            return

        # antialiasing makes things look nicer :)
        painter.setRenderHint(QPainter.Antialiasing)

        self.toView.x()
        pM1 = QPointF(self.fromView.x() + self.fromView.size().width() / 2,
                      self.fromView.y() + self.fromView.size().height() / 2)
        pM2 = QPointF(self.toView.x() + self.toView.size().width() / 2,
                      self.toView.y() + self.toView.size().height() / 2)
        deltaX = pM2.x() - pM1.x()
        deltaY = pM2.y() - pM1.y()
        if deltaX == 0:
            deltaX = 0.01
        if deltaY == 0:
            deltaY = 0.01
        if deltaX >= 0:
            if deltaY >= 0:
                # rechts unten
                if deltaX / deltaY >= self.fromView.size().width() / self.fromView.size().height():
                    # Start von rechter Seite
                    pStart = QPointF(pM1.x() + self.fromView.size().width() / 2,
                                     pM1.y() + (self.fromView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Start von unterer Seite
                    pStart = QPointF(pM1.x() + (self.fromView.size().height() / 2) * (deltaX / deltaY),
                                     pM1.y() + self.fromView.size().height() / 2)

                if deltaX / deltaY >= self.toView.size().width() / self.toView.size().height():
                    # Ende bei linker Seite
                    pEnd = QPointF(pM2.x() - self.toView.size().width() / 2,
                                   pM2.y() - (self.toView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Ende bei oberer Seite
                    pEnd = QPointF(pM2.x() - (self.toView.size().height() / 2) * (deltaX / deltaY),
                                   pM2.y() - self.toView.size().height() / 2)
            else:
                # rechts oben
                if deltaX / deltaY * -1 >= self.fromView.size().width() / self.fromView.size().height():
                    # Start von rechter Seite
                    pStart = QPointF(pM1.x() + self.fromView.size().width() / 2,
                                     pM1.y() + (self.fromView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Start von oberer Seite
                    pStart = QPointF(pM1.x() - (self.fromView.size().height() / 2) * (deltaX / deltaY),
                                     pM1.y() - self.fromView.size().height() / 2)

                if deltaX / deltaY * -1 >= self.toView.size().width() / self.toView.size().height():
                    # Ende bei linker Seite
                    pEnd = QPointF(pM2.x() - self.toView.size().width() / 2,
                                   pM2.y() - (self.toView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Ende bei unterer Seite
                    pEnd = QPointF(pM2.x() + (self.toView.size().height() / 2) * (deltaX / deltaY),
                                   pM2.y() + self.toView.size().height() / 2)
        else:
            if deltaY >= 0:
                # links unten
                if deltaX / deltaY * -1 >= self.fromView.size().width() / self.fromView.size().height():
                    # Start von linker Seite
                    pStart = QPointF(pM1.x() - self.fromView.size().width() / 2,
                                     pM1.y() - (self.fromView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Start von unterer Seite
                    pStart = QPointF(pM1.x() + (self.fromView.size().height() / 2) * (deltaX / deltaY),
                                     pM1.y() + self.fromView.size().height() / 2)

                if deltaX / deltaY * -1 >= self.toView.size().width() / self.toView.size().height():
                    # Ende bei rechten Seite
                    pEnd = QPointF(pM2.x() + self.toView.size().width() / 2,
                                   pM2.y() + (self.toView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Ende bei oberer Seite
                    pEnd = QPointF(pM2.x() - (self.toView.size().height() / 2) * (deltaX / deltaY),
                                   pM2.y() - self.toView.size().height() / 2)
            else:
                # links oben
                if deltaX / deltaY >= self.fromView.size().width() / self.fromView.size().height():
                    # Start von linker Seite
                    pStart = QPointF(pM1.x() - self.fromView.size().width() / 2,
                                     pM1.y() - (self.fromView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Start von oberer Seite
                    pStart = QPointF(pM1.x() - (self.fromView.size().height() / 2) * (deltaX / deltaY),
                                     pM1.y() - self.fromView.size().height() / 2)

                if deltaX / deltaY >= self.toView.size().width() / self.toView.size().height():
                    # Ende bei rechter Seite
                    pEnd = QPointF(pM2.x() + self.toView.size().width() / 2,
                                   pM2.y() + (self.toView.size().width() / 2) * (deltaY / deltaX))
                else:
                    # Ende bei unterer Seite
                    pEnd = QPointF(pM2.x() + (self.toView.size().height() / 2) * (deltaX / deltaY),
                                   pM2.y() + self.toView.size().height() / 2)

        self.setLine(QLineF(pEnd, pStart))

        if self.line().length() != 0:
            angle = math.acos(self.line().dx() / self.line().length())
            if self.line().dy() >= 0:
                angle = math.pi * 2 - angle

            arrowP1 = self.line().p1() + QPointF(math.sin(angle + math.pi / 2.5) * self.arrowSize, math.cos(angle + math.pi / 2.5) * self.arrowSize)
            arrowP2 = self.line().p1() + QPointF(math.sin(angle + math.pi - math.pi / 2.5) * self.arrowSize, math.cos(angle + math.pi - math.pi / 2.5) * self.arrowSize)
            self.arrowhead.clear()
            self.arrowhead.append(self.line().p1())
            self.arrowhead.append(arrowP1)
            self.arrowhead.append(arrowP2)
            painter.setBrush(QBrush(self.bgcolor))
            painter.drawLine(self.line())
            painter.drawPolygon(self.arrowhead)

    def delete(self):
        """ removes the pointer from the DataGraph """
        self.toView.incomingPointers.remove(self)
        self.fromView.outgoingPointers.remove(self)
        self.distributedObjects.datagraphController.removePointer(self)

    def setX(self, _):
        logging.error("Ignoring setting our Pointer's x position")

    def setY(self, _):
        logging.error("Ignoring setting our Pointer's y position")
