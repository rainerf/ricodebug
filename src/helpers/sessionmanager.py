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

from PyQt4.QtCore import QObject, QIODevice, QFile, QString
from PyQt4.QtGui import QDialog, QGridLayout, QCheckBox, QPushButton, QFileDialog
from os.path import exists
from PyQt4.QtXml import QDomDocument, QDomElement, QDomNode
import logging


class SessionManager(QObject):
    """ Class owns an XmlHandler to write session info to file.
        Objects register with Sessionmanager by calling emitRegisterWithSessionManager from signalproxy.
        Registered Objects must implement a loadSession(self, XmlHandler) and saveSession(self, XmlHandler) method.
        In these mehods they have r/w access to xml file to save their debug info.
    """
    def __init__(self, distributedObjects, parent=None):
        """Init Session Manager"""
        QObject.__init__(self)
        self.distributedObjects = distributedObjects
        self.sessionRootName = "ricodebugSession"

        ## XmlHandler, used for saving session info to xml
        self.xmlHandler = XmlHandler(self.distributedObjects, self.sessionRootName)

        self.registeredObjects = {}
        self.saveSessionDlg = SaveSessionDialog(parent, self)
        distributedObjects.signalProxy.registerWithSessionManager.connect(self.register)

    def register(self, regObject, dialogItem=None):
        if dialogItem == None:
            self.registeredObjects["obj" + len(self.registeredObjects)] = regObject
        elif not self.registeredObjects. has_key(dialogItem):
            self.saveSessionDlg.addDialogItem(dialogItem)
            self.registeredObjects[dialogItem] = regObject

    def showSaveSessionDialog(self):
        self.saveSessionDlg.show()

    def showRestoreSessionDialog(self):
        filename = str(QFileDialog.getOpenFileName(None, "Restore Session", QString(), "*.xml"))
        if (filename != ""):
            self.restoreSession(filename)

    def saveSession(self, filename, cbContainer):
        ''' Save breakpoints, watches and tracepoints of session '''
        #create node for executable
        self.xmlHandler.clear()
        self.xmlHandler.createNode("executable", None, {"name": self.distributedObjects.debugController.getExecutableName()})

        # tell registered controllers to save session info
        for cb in cbContainer:
            if cb.isChecked():
                #print cb.text()
                key = str(cb.text())
                if self.registeredObjects. has_key(key):
                    self.xmlHandler.createNode("save" + key)
                    try:
                        self.registeredObjects[key].saveSession(self.xmlHandler)
                    except:
                        logging.error("Could not save session. Registered object %s does not implement a valid saveSession() method.", key)

        self.xmlHandler.save(filename)

    def restoreSession(self, filename):
        ''' Load breakpoints, watches and tracepoints of session '''
        if self.xmlHandler.load(filename):
            if self.xmlHandler.getNode(self.sessionRootName) != None:

                exeNode = self.xmlHandler.getNode("executable")
                exeName = self.xmlHandler.getAttributes(exeNode)['name']

                if (exists(exeName)):
                    self.distributedObjects.debugController.openExecutable(exeName)

                    for dialogItem, regObject in self.registeredObjects.iteritems():
                        if self.xmlHandler.getNode("save" + dialogItem) != None:
                            try:
                                regObject.loadSession(self.xmlHandler)
                            except:
                                logging.error("Could not load session. Registered object %s does not implement a valid loadSession() method.", dialogItem)

                else:
                    logging.error("Cannot restore session - Executable %s specified in XML file does not exist.", exeName)


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
        self.okButton.released.connect(self.__showSaveFileDialog)

    def addDialogItem(self, dialogItem):
        cb = QCheckBox(dialogItem, self)
        cb.setChecked(True)
        self.layout.addWidget(cb, len(self.cbContainer), 0)
        self.setLayout(self.layout)
        self.cbContainer.append(cb)

    def __showSaveFileDialog(self):
        filename = str(QFileDialog.getSaveFileName(None, "Save Session", QString(), "*.xml"))
        if (filename != ""):
            self.SessionManager.saveSession(filename, self.cbContainer)
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
    def __init__(self, distributedObjects, rootname):
        self.Xml = QDomDocument("xmldoc")
        self.rootname = rootname
        self.rootNode = QDomElement()
        self.clear()

    def createNode(self, nodeName, parentNode=None, withAttribs={}):
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

    def getNode(self, nodeName, parent=None):
        ''' Get first xml node by name
            @return QDomElement '''
        if isinstance(nodeName, str) and len(nodeName) != 0:
            if parent == None or not isinstance(parent, QDomNode):
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
        if not filename.endswith(".xml"):
            filename = filename + ".xml"

        file_object = QFile(filename)
        if not file_object.open(QIODevice.WriteOnly):
            logging.error("File %s could not be opened.", filename)
        else:
            file_object.writeData(self.Xml.toString())
            file_object.close()

    def clear(self):
        ''' Clear xml doc and reset root node'''
        self.Xml.clear()
        self.rootNode = self.Xml.createElement(self.rootname)
        self.Xml.appendChild(self.rootNode)

    def load(self, filename):
        """Loads session info from xml file. Returns false if loading fails, true otherwise."""
        if not exists(filename):
            logging.error("Cannot restore session - File %s not found.", filename)
            return False

        file_object = QFile(filename)
        self.Xml.clear()
        if not file_object.open(QIODevice.ReadOnly):
            logging.error("File %s could not be opened.", filename)
            return False
        else:
            if not self.Xml.setContent(file_object.readAll()):
                logging.error("self.Xml.setContent() failed.")
                file_object.close()
                return False

            file_object.close()
            self.rootNode = self.Xml.documentElement()
            return True
