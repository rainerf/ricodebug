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

from PyQt4.QtGui import QGraphicsPolygonItem, QColor, QPolygonF, QBrush, QPen
from PyQt4.QtCore import QObject, QPointF, SIGNAL

class Pointer(QGraphicsPolygonItem):
    """ QGraphicsPolygonItem to model a Pointer as an Arrow from a Pointer-Variable to its Content. """
    fgcolor = QColor(0,0,0)
    bgcolor = QColor(255,255,255)

    def __init__(self, parent, fromView, toView, distributedObjects):
        """ Constructor
        @param parent                parent for the QGraphicsPolygonItem-Constructor
        @param fromView              datagraph.htmlvariableview.HtmlVariableView, starting point of the Pointer
        @param toView                datagraph.htmlvariableview.HtmlVariableView, end point of the Pointer
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        fromView and toView are QGraphicsWebViews
        """
        QGraphicsPolygonItem.__init__(self, parent)
        self.fromView = fromView
        fromView.addOutgoingPointer(self)
        self.toView = toView
        toView.addIncomingPointer(self)
        self.distributedObjects = distributedObjects
        self.setBrush( QBrush( self.bgcolor  ) )
        self.setPen( QPen(self.fgcolor,1) )
        QObject.connect(self.fromView, SIGNAL('geometryChanged()'), self.render)
        QObject.connect(self.toView, SIGNAL('geometryChanged()'), self.render)
        QObject.connect(self.fromView, SIGNAL('xChanged()'), self.render)
        QObject.connect(self.fromView, SIGNAL('yChanged()'), self.render)
        QObject.connect(self.toView, SIGNAL('xChanged()'), self.render)
        QObject.connect(self.toView, SIGNAL('yChanged()'), self.render)
        QObject.connect(self.fromView, SIGNAL('deleting()'), self.delete)
        QObject.connect(self.toView, SIGNAL('deleting()'), self.delete)
        
        self.render()
        
    def getFromView(self):
        return self.fromView
    
    def getToView(self):
        return self.toView
    
    def render(self):
        """ Main-Method of the Pointer-Class <br>
            calculates/renders/draws the Lines of the Arrow
        """
        points = QPolygonF()
        self.toView.x()
        pM1 = QPointF(self.fromView.x() + self.fromView.size().width()/2,
                      self.fromView.y() + self.fromView.size().height()/2)
        pM2 = QPointF(self.toView.x() + self.toView.size().width()/2,
                      self.toView.y() + self.toView.size().height()/2)
        deltaX = pM2.x()-pM1.x()
        deltaY = pM2.y()-pM1.y()
        if deltaX == 0:
            deltaX = 0.01 
        if deltaY == 0:
            deltaY = 0.01
        if deltaX >= 0:
            if deltaY >= 0:
                # rechts unten
                if deltaX/deltaY >= self.fromView.size().width()/self.fromView.size().height():
                    # Start von rechter Seite
                    pStart = QPointF(pM1.x() + self.fromView.size().width()/2,
                                     pM1.y() + (self.fromView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Start von unterer Seite
                    pStart = QPointF(pM1.x() + (self.fromView.size().height()/2)*(deltaX/deltaY),
                                     pM1.y() + self.fromView.size().height()/2)
                
                if deltaX/deltaY >= self.toView.size().width()/self.toView.size().height():
                    # Ende bei linker Seite
                    pEnd = QPointF(pM2.x() - self.toView.size().width()/2,
                                   pM2.y() - (self.toView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Ende bei oberer Seite
                    pEnd = QPointF(pM2.x() - (self.toView.size().height()/2)*(deltaX/deltaY),
                                   pM2.y() - self.toView.size().height()/2)
            else:
                # rechts oben
                if deltaX/deltaY*-1 >= self.fromView.size().width()/self.fromView.size().height():
                    # Start von rechter Seite
                    pStart = QPointF(pM1.x() + self.fromView.size().width()/2,
                                     pM1.y() + (self.fromView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Start von oberer Seite
                    pStart = QPointF(pM1.x() - (self.fromView.size().height()/2)*(deltaX/deltaY),
                                     pM1.y() - self.fromView.size().height()/2)
                
                if deltaX/deltaY*-1 >= self.toView.size().width()/self.toView.size().height():
                    # Ende bei linker Seite
                    pEnd = QPointF(pM2.x() - self.toView.size().width()/2,
                                   pM2.y() - (self.toView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Ende bei unterer Seite
                    pEnd = QPointF(pM2.x() + (self.toView.size().height()/2)*(deltaX/deltaY),
                                   pM2.y() + self.toView.size().height()/2)
        else:
            if deltaY >= 0:
                # links unten
                if deltaX/deltaY*-1 >= self.fromView.size().width()/self.fromView.size().height():
                    # Start von linker Seite
                    pStart = QPointF(pM1.x() - self.fromView.size().width()/2,
                                     pM1.y() - (self.fromView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Start von unterer Seite
                    pStart = QPointF(pM1.x() + (self.fromView.size().height()/2)*(deltaX/deltaY),
                                     pM1.y() + self.fromView.size().height()/2)
                
                if deltaX/deltaY*-1 >= self.toView.size().width()/self.toView.size().height():
                    # Ende bei rechten Seite
                    pEnd = QPointF(pM2.x() + self.toView.size().width()/2,
                                   pM2.y() + (self.toView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Ende bei oberer Seite
                    pEnd = QPointF(pM2.x() - (self.toView.size().height()/2)*(deltaX/deltaY),
                                   pM2.y() - self.toView.size().height()/2)
            else:
                # links oben
                if deltaX/deltaY >= self.fromView.size().width()/self.fromView.size().height():
                    # Start von linker Seite
                    pStart = QPointF(pM1.x() - self.fromView.size().width()/2,
                                     pM1.y() - (self.fromView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Start von oberer Seite
                    pStart = QPointF(pM1.x() - (self.fromView.size().height()/2)*(deltaX/deltaY),
                                     pM1.y() - self.fromView.size().height()/2)
                
                if deltaX/deltaY >= self.toView.size().width()/self.toView.size().height():
                    # Ende bei rechter Seite
                    pEnd = QPointF(pM2.x() + self.toView.size().width()/2,
                                   pM2.y() + (self.toView.size().width()/2)*(deltaY/deltaX))
                else:
                    # Ende bei unterer Seite
                    pEnd = QPointF(pM2.x() + (self.toView.size().height()/2)*(deltaX/deltaY),
                                   pM2.y() + self.toView.size().height()/2)
        
        #pStart = QPointF(self.fromView.x() + self.fromView.size().width(),
        #                 self.fromView.y() + self.fromView.size().height()/2)
        #pEnd = QPointF(self.toView.x(), self.toView.y() + self.toView.size().height()/2)
        p1 = pStart
        p2 = QPointF(pEnd.x()-(pEnd.x()-pStart.x())/7, pEnd.y()-(pEnd.y()-pStart.y())/7)
        p3 = QPointF(p2.x()-(p2.y()-p1.y())/20, p2.y()+(p2.x()-p1.x())/20)
        p4 = pEnd
        p5 = QPointF(p2.x()+(p2.y()-p1.y())/20, p2.y()-(p2.x()-p1.x())/20)
        p6 = p2
        points.append(p1)
        points.append(p2)
        points.append(p3)
        points.append(p4)
        points.append(p5)
        points.append(p6)
        self.setPolygon(points)
    
    def delete(self):
        """ removes the pointer from the DataGraph """
        self.distributedObjects.datagraph_controller.removePointer(self)
