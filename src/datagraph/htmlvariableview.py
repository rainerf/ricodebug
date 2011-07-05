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
from PyQt4.QtGui import QGraphicsItem, QCursor
from PyQt4.QtWebKit import QGraphicsWebView, QWebPage
from mako.template import Template
from PyQt4 import QtCore
import sys

class TestObj(QtCore.QObject):
    @QtCore.pyqtSlot()
    def testSlot(self):
        print "testSlot called"

class HtmlVariableView(QGraphicsWebView):
    """ the view to show variables in the DataGraph """
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var                datagraph.datagraphvw.DataGraphVW, holds the Data of the Variable to show
        @param distributedObjects distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QGraphicsWebView.__init__(self, None)
        self.var = var
        self.distributedObjects = distributedObjects
        self.templateHandlers = []
        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/htmlvariableview.mako')
        self.page().setPreferredContentsSize(QSize(0,0))
        self.setPreferredSize(QSizeF(0, 0))
        self.setResizesToContents(True)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks);
        self.connect(self.page(), SIGNAL('linkClicked(QUrl)'), self.linkClicked, Qt.DirectConnection)
        self.connect(self.var, SIGNAL('changed()'), self.render)
        self.incomingPointers = []
        self.outgoingPointers = []
        
        self.source = None
        
        # ids for ourself and the template handlers we will eventually render
        self.lastId = -1
        self.uniqueIds = {}
        
        self.dirty = True
        
        self.id = self.getUniqueId(self)
        
        self.render()
        
    def getIncomingPointers(self):
        return self.incomingPointers
    
    def getOutgoingPointers(self):
        return self.outgoingPointers
        
    def addIncomingPointer(self, pointer):
        self.incomingPointers.append(pointer)
        
    def addOutgoingPointer(self, pointer):
        self.outgoingPointers.append(pointer)
    
    def setDirty(self):
        self.dirty = True
        self.render()   # FIXME: defer rendering until all changed()-events from variables have been processed
    
    def render(self):
        if self.dirty:
            self.source = self.htmlTemplate.render(var=self.var, view=self, top=True, parentHandler=self, id=self.id)
            # the page's viewport will not shrink if new content is set, so set it to it's minimum
            self.page().setViewportSize(QSize(0, 0))
            
            self.setHtml(self.source)
            for template, id in self.uniqueIds.iteritems():
                self.page().mainFrame().addToJavaScriptWindowObject(id, template)
            self.dirty = False
            print self.source
        
        return self.source
    
    def linkClicked(self, url):
        self.handleCommand(str(url.toString()))
    
    def prepareContextMenu(self, menu):
        menu.addAction("Remove %s" % self.var.variable.exp)
        menu.addAction("Show HTML for %s" % self.var.variable.exp, self.showHtml)
    
    @QtCore.pyqtSlot()
    def showHtml(self):
        print self.source
    
    def showContextMenu(self, menu):
        menu.exec_(QCursor.pos())
    
    def contextMenuEvent(self, event):
        pass
    #    self.menu.exec_()
    #    print "contextMenuEvent", self.handlerForContextMenu, self.handlerForContextMenu.var.variable.exp
    #    menu = QMenu()
    #    menu.addAction("Delete %s" % self.var.getTemplateHandler().var.variable.exp)
    #    menu.addAction("Set filter for %s" % self.handlerForContextMenu.var.variable.exp)
    #    menu.exec_()
        
    # this needs to be defined as a slot so it can be called from javascript
#    @QtCore.pyqtSlot(str)
#    def handleCommand(self, command):
#        parts = command.split(";")
#        assert(len(parts) == 2)
#        var = parts[0]
#        command = parts[1]
#        self.findHandlerForStr(var).linkClicked(command, self)
#        self.render()
#    
#    def findHandlerForStr(self, var):
#        # find handler to handle link
#        for handler in self.templateHandlers:
#            if (str(handler.var) == var):
#                return handler
#        return None
    
    
    def onDelete(self):
        self.emit(SIGNAL('deleting()'))

    def getUniqueId(self, template):
        if not template in self.uniqueIds:
            self.lastId += 1
            self.uniqueIds[template] = "tmpl%d" % self.lastId
        return self.uniqueIds[template]

# def paint(self, painter, option, widget):
#    from PyQt4.QtGui import QColor
#    painter.setPen(QColor(Qt.red))
#    painter.drawRoundedRect(self.boundingRect(), 5, 5)
#    QGraphicsWebView.paint(self, painter, option, widget)
