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

from PyQt4.QtCore import SIGNAL, QObject, QIODevice, QFile, QString
from PyQt4.QtGui import QDialog, QGridLayout, QCheckBox, QPushButton, QFileDialog
from os.path import exists
from PyQt4.QtXml import QDomDocument, QDomElement, QDomNode
from logger import Logger
      
class SessionManager(QObject):
    """ Class owns an XmlHandler to write session info to file.
        Objects register with Sessionmanager by calling emitRegisterWithSessionManager from signalproxy.
        Registered Objects must implement a loadSession(self, XmlHandler) and saveSession(self, XmlHandler) method.
        In these mehods they have r/w access to xml file to save their debug info.
    """
    def __init__(self, distributed_objects, parent = None):
        """Init Session Manager"""
        QObject.__init__(self)
        self.distributed_objects = distributed_objects
        self.sessionRootName = "ricodebugSession"
        
        ## XmlHandler, used for saving session info to xml
        self.xmlHandler = XmlHandler(self.distributed_objects, self.sessionRootName)
        
        self.registeredObjects = {}
        self.saveSessionDlg = SaveSessionDialog(parent, self)
        QObject.connect(distributed_objects.signal_proxy, SIGNAL('registerWithSessionManager(PyQt_PyObject, PyQt_PyObject)'), self.register)
            
    def register(self, regObject, dialogItem=None):
        if dialogItem == None:
            self.registeredObjects["obj"+len(self.registeredObjects)] = regObject  
        elif not self.registeredObjects.has_key(dialogItem):
            self.saveSessionDlg.addDialogItem(dialogItem)
            self.registeredObjects[dialogItem] = regObject
    
    def showSaveSessionDialog(self):
        self.saveSessionDlg.show()
        
    def showRestoreSessionDialog(self):
        filename = str(QFileDialog.getOpenFileName(None, "Restore Session", QString(), "*.xml"))
        if (filename != ""):
            self.restoreSession(filename)           
                    
    def saveSession(self, filename, cbContainer):#saveBreakpoints = True, saveTracepoints = True, saveWatches = True, saveGraph = True):
        ''' Save breakpoints, watches and tracepoints of session '''        
        #create node for executable
        self.xmlHandler.clear()
        self.xmlHandler.createNode("executable", None, {"name": self.distributed_objects.debug_controller.getExecutableName()})  
        
        # tell registered controllers to save session info
        for cb in cbContainer:
            if cb.isChecked():
                #print cb.text()
                key = str(cb.text())
                if self.registeredObjects.has_key(key):
                    self.xmlHandler.createNode("save" + key)
                    try:
                        self.registeredObjects[key].saveSession(self.xmlHandler)
                    except:
                        self.Logger.addLogMessage("SessionManager", "Could not save session. Registered object " + key + " does not implement a valid saveSession() method.", Logger.MSG_TYPE_ERROR)
                
        self.xmlHandler.save(filename)
        
            
    def restoreSession(self, filename):
        ''' Load breakpoints, watches and tracepoints of session '''
        if self.xmlHandler.load(filename) == True:
            if self.xmlHandler.getNode(self.sessionRootName) != None:
                
                exeNode = self.xmlHandler.getNode("executable")                
                exeName = self.xmlHandler.getAttributes(exeNode)['name']
                    
                if (exists(exeName)):
                    self.distributed_objects.debug_controller.openExecutable(exeName)
                    
                    for dialogItem, regObject in self.registeredObjects.iteritems():
                        if self.xmlHandler.getNode("save" + dialogItem) != None:
                            try:
                                regObject.loadSession(self.xmlHandler)
                            except:
                                self.Logger.addLogMessage("SessionManager", "Could not load session. Registered object " + dialogItem + " does not implement a valid loadSession() method.", Logger.MSG_TYPE_ERROR)
                
                else:
                    self.Logger.addLogMessage("xmlHandler", "Cannot restore session - Executable " + exeName + " specified in XML file does not exist.", Logger.MSG_TYPE_ERROR, True)
                
                
                  
class SaveSessionDialog(QDialog):
    ''' Dialog window. Allows user to choose session info to save. '''
    def __init__(self, parent, sessionmgr):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Save Session")
        
        self.cbContainer = []   
        self.layout = QGridLayout()
        self.okButton = QPushButton("Ok", self)
        self.layout.addWidget(self.okButton, 0, 2)        
        self.setLayout(self.layout)        
        self.SessionManager = sessionmgr
        QObject.connect(self.okButton, SIGNAL("released()"), self.__showSaveFileDialog)
         
    def addDialogItem(self, dialogItem):
        cb = QCheckBox(dialogItem, self)
        cb.setChecked(True)
        self.layout.addWidget(cb, len(self.cbContainer), 0)
        self.setLayout(self.layout)
        self.cbContainer.append(cb)
        
    def __showSaveFileDialog(self):    
        filename = str(QFileDialog.getSaveFileName(None, "Save Session", QString(), "*.xml")) 
        if (filename != ""):
            self.SessionManager.saveSession(filename, self.cbContainer)#self.breakpointsCB.isChecked(), self.tracepointsCB.isChecked(), self.watchesCB.isChecked(), self.graphCB.isChecked())
        self.close()
        
class RestoreSessionDialog(QObject):
    '''Open file dialog which additionally loads the session's executable'''
    def __init__(self, parent, sessionmgr):
        QObject.__init__(self, parent)
        self.sessionmgr = sessionmgr
        
    def show(self):
        filename = str(QFileDialog.getOpenFileName(None, "Restore Session", QString(), "*.xml"))
        if (filename != ""):
            self.sessionmgr.restoreSession(filename)
      
        
class XmlHandler():
    ''' Handler used to save session info to an xml file. '''
    def __init__(self, distributed_objects, rootname):      
        self.Xml = QDomDocument("xmldoc")
        self.rootname = rootname
        self.rootNode = QDomElement()
        self.clear()
                
    def createNode(self, nodeName, parentNode = None, withAttribs = {}):
        ''' Create and insert node
            @param nodeName: String representing name of node
            @param parentNode: QDomElement representing parent node. Root will be parent if this is None
            @param withAttribs: dict with node attributes
            @return node on success, None on error '''
        if isinstance(nodeName, str) and len(nodeName) != 0:
            node = self.Xml.createElement(nodeName)
            
            if isinstance(withAttribs, dict) and withAttribs != {}:
                for key, value in withAttribs.items():
                    node.setAttribute(key, value)
                        
            if parentNode == None:
                self.rootNode.appendChild(node)
            else:
                if isinstance(parentNode, QDomElement):
                    parentNode.appendChild(node)
            
            return node   
        return None 
    
    def getNode(self, nodeName, parent = None): 
        ''' Get first xml node by name
            @return QDomElement '''
        if isinstance(nodeName, str) and len(nodeName) != 0:
            if parent == None or isinstance(parent, QDomNode) == False:
                return self.rootNode.firstChildElement(nodeName)
            else:
                return parent.firstChildElement(nodeName)
    
    def getAttributes(self, node):
        ''' Get a dict with attributes of node
            @param node: QDomElement
            @return dict(QString, QString) with attributes '''
        attribs = {}
        if isinstance(node, QDomElement) or isinstance(node, QDomNode):
            namedNodeMap = node.attributes()
            for i in xrange(namedNodeMap.count()):
                item = namedNodeMap.item(i)
                attribs[str(item.nodeName())] = str(item.nodeValue())
        return attribs
        
    def save(self, filename):
        """Writes session info to xml file. Overwrites existing files"""
        if filename.endswith(".xml") == False:
            filename = filename + ".xml"
            
        file_object = QFile(filename)
        if (file_object.open(QIODevice.WriteOnly) == False):
            Logger.getInstance().addLogMessage("xmlHandler", "File " + filename + " could not be opened.", Logger.MSG_TYPE_ERROR, True)
        else:
            str = self.Xml.toString()  
            file_object.writeData(self.Xml.toString())
            file_object.close()
    
    def clear(self):
        ''' Clear xml doc and reset root node'''
        self.Xml.clear()
        self.rootNode = self.Xml.createElement(self.rootname)
        self.Xml.appendChild(self.rootNode)       
    
    def load(self, filename):
        """Loads session info from xml file. Returns false if loading fails, true otherwise."""
        if (exists(filename) == False):
            Logger.getInstance().addLogMessage("xmlHandler", "Cannot restore session - File " + filename + " not found.", Logger.MSG_TYPE_ERROR, True)
            return False
                
        file_object = QFile(filename)
        self.Xml.clear()
        if (file_object.open(QIODevice.ReadOnly) == False):
            Logger.getInstance().addLogMessage("xmlHandler", "File " + filename + " could not be opened.", Logger.MSG_TYPE_ERROR, True)
            return False
        else:  
            if (self.Xml.setContent(file_object.readAll()) == False):
                Logger.getInstance().addLogMessage("xmlHandler", "self.Xml.setContent() failed.", Logger.MSG_TYPE_ERROR, True)
                file_object.close()
                return False
            
            file_object.close()
            self.rootNode = self.Xml.documentElement()
            return True  
        
      




        

        