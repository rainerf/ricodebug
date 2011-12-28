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

from PyQt4.QtCore import SIGNAL, QSize, QSizeF, Qt
from PyQt4.QtGui import QGraphicsItem, QCursor, QFileDialog, QIcon
from PyQt4.QtWebKit import QGraphicsWebView, QWebPage
from mako.template import Template
from PyQt4 import QtCore
import StringIO
import sys
import logging

class HtmlVariableView(QGraphicsWebView):
    """ the view to show variables in the DataGraph """
    
    def __init__(self, varWrapper, distributedObjects):
        """ Constructor
        @param varWrapper                datagraph.datagraphvw.DataGraphVW, holds the Data of the Variable to show
        @param distributedObjects distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QGraphicsWebView.__init__(self, None)
        self.varWrapper = varWrapper
        self.distributedObjects = distributedObjects
        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/templates/htmlvariableview.mako')
        self.page().setPreferredContentsSize(QSize(0,0))
        self.setPreferredSize(QSizeF(0, 0))
        self.setResizesToContents(True)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks);
        self.connect(self.page(), SIGNAL('linkClicked(QUrl)'), self.linkClicked, Qt.DirectConnection)
        self.incomingPointers = []
        self.outgoingPointers = []
        
        self.source = None
        
        # ids for ourself and the template handlers we will eventually render
        self.lastId = -1
        self.uniqueIds = {}
        
        self.dirty = True
        
        self.id = self.getUniqueId(self)
        
        self.connect(self.distributedObjects.signal_proxy, SIGNAL("variableUpdateCompleted()"), self.render)
        
    def getIncomingPointers(self):
        return self.incomingPointers
    
    def getOutgoingPointers(self):
        return self.outgoingPointers
        
    def addIncomingPointer(self, pointer):
        self.incomingPointers.append(pointer)
        
    def addOutgoingPointer(self, pointer):
        self.outgoingPointers.append(pointer)
    
    def setDirty(self, render_immediately):
        self.dirty = True
        if render_immediately:
            self.render()
    
    def render(self):
        if self.dirty:
            # the page's viewport will not shrink if new content is set, so set it to it's minimum
            self.page().setViewportSize(QSize(0, 0))
            try:
                self.source = self.htmlTemplate.render(varWrapper=self.varWrapper, top=True, id=self.id)
                self.setHtml(self.source)
                
                for template, id_ in self.uniqueIds.iteritems():
                    self.page().mainFrame().addToJavaScriptWindowObject(id_, template)
            except Exception as e:
                logging.error("Rendering failed: %s", str(e))
                self.setHtml(str(e))
                raise
            
            # force an update of the scene that contains us, since sometimes setHtml
            # will not cause the view to be redrawn immediately
            if self.scene():
                self.scene().update()
            
            self.dirty = False
        
        return self.source
    
    def linkClicked(self, url):
        self.handleCommand(str(url.toString()))
    
    def openContextMenu(self, menu):
        menu.addAction(QIcon(":/icons/images/minus.png"), "Remove %s" % self.varWrapper.getExp(), self.remove)
        menu.addAction(QIcon(":/icons/images/save-html.png"), "Save HTML for %s" % self.varWrapper.getExp(), self.saveHtml)
        menu.exec_(QCursor.pos())
    
    @QtCore.pyqtSlot()
    def saveHtml(self):
        name = QFileDialog.getSaveFileName(filter="HTML (*.html)")
        if name != "":
            out = file(name, 'w')
            out.write(self.source)
            out.close()
    
    def contextMenuEvent(self, event):
        pass

    @QtCore.pyqtSlot()
    def remove(self):
        """remove the varWrapper from the datagraph"""
        self.emit(SIGNAL('removing()'))
        self.distributedObjects.datagraph_controller.removeVar(self.varWrapper)
    
    def getUniqueId(self, template):
        if not template in self.uniqueIds:
            self.lastId += 1
            self.uniqueIds[template] = "tmpl%d" % self.lastId
        return self.uniqueIds[template]

#    def paint(self, painter, option, widget):
#        from PyQt4.QtGui import QColor
#        painter.setPen(QColor(Qt.red))
#        painter.drawRoundedRect(self.boundingRect(), 5, 5)
#        QGraphicsWebView.paint(self, painter, option, widget)

