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
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtWebKit import QGraphicsWebView, QWebPage
from mako.template import Template
import sys

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
        
        self.render()
        
    def getIncomingPointers(self):
        return self.incomingPointers
    
    def getOutgoingPointers(self):
        return self.outgoingPointers
        
    def addIncomingPointer(self, pointer):
        self.incomingPointers.append(pointer)
        
    def addOutgoingPointer(self, pointer):
        self.outgoingPointers.append(pointer)
    
    def render(self):
        self.templateHandlers = []
        self.html = self.htmlTemplate.render(var=self.var, handlers=self.templateHandlers)
        # the page's viewport will not shrink if new content is set, so set it to it's minimum
        self.page().setViewportSize(QSize(0, 0)) 
        self.setHtml(self.html)
        return self.html
    
    def linkClicked(self, url):
        urlStr = str(url.toString())
        print "htmlvarview: link clicked: " + urlStr
        urlStrParts = urlStr.split(';')
        assert(len(urlStrParts) >= 2)
        varStr = urlStrParts[0]
        #commandStr = urlStrParts[1]
        
        # find handler to handle link
        for handler in self.templateHandlers:
            if (varStr == str(handler.var)):
                handler.linkClicked(url, self)
        self.render()
    
    def onDelete(self):
        self.emit(SIGNAL('deleting()'))

    def paint(self, painter, option, widget):
        #from PyQt4.QtGui import QColor
        #painter.setPen(QColor(Qt.red))
        #painter.drawRoundedRect(self.boundingRect(), 5, 5)
        QGraphicsWebView.paint(self, painter, option, widget)

