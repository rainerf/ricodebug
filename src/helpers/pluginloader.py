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

import os
from PyQt4.QtCore import SIGNAL, QObject, QIODevice, QFile
from PyQt4.QtGui import QAction
from PyQt4.QtXml import QDomDocument
from logger import Logger


class PluginAction(QAction):
    """ Class extends QAction to load a plugin over a menu entry."""
    def __init__(self, parent, path):
        self.pluginldr = parent
        QAction.__init__(self, parent)
        self.path = path
        self.setObjectName("actionPlugin" + os.path.basename(path)[:-3])
        self.setCheckable(True)
        self.setChecked(False)

        # get dir name
        self.dirname = os.path.dirname(path)[os.path.dirname(path).rfind('/') + 1:]

        # import name of plugin from __init__.py
        try:
            d = __import__('plugins.' + self.dirname)
            self.setText(d.PluginName)
        except ImportError:
            Logger.getInstance().addLogMessage("PluginAction", "No module named " + self.dirname + " found", Logger.MSG_TYPE_ERROR)
        except AttributeError:
            Logger.getInstance().addLogMessage("PluginAction", "Error finding name of plugin " + self.path + ". No PluginName function found", Logger.MSG_TYPE_ERROR)
            #if PluginName is not defined, name plugin like file
            self.setText(os.path.basename(path))

        #connect action to initPlugin() and deInitPlugin methods
        QObject.connect(self, SIGNAL('toggled(bool)'), self.__togglePlugin)

    def __togglePlugin(self, checked):
        ''' Load/Unload Plugin by toggling menu entries '''
        if checked == True:
            self.pluginldr.loadPlugin(self.path)
        else:
            self.pluginldr.unloadPlugin(self.path)


class PluginLoader(QObject):
    '''PluginLoader.
        Goes through subfolders of /plugins and searches for plugin files(ending with "plugin.py").
        SamplePlugin provides a sample for such plugins.
    '''

    def __init__(self, distributed_objects):
        """CTOR of pluginloader."""
        QObject.__init__(self)
        self.plugin_dir = os.path.dirname(__file__) + '/../plugins'

        #contains loaded plugin modules
        self.plugins = {}

        #contains actions from mainwindow
        self.pluginActions = []

        #signalproxy for communication with plugins
        self.signalproxy = distributed_objects.signalProxy

        #xml file for plugin info
        self.xmlFile = self.plugin_dir + '/plugins.xml'

    def addAvailablePlugins(self):
        """Search in all subfolders of src/plugins for plugin files and add them as menu entries."""
        #go through subdirs of pluginfolder and identify pluginfiles (ending with "Plugins.py")
        for root, _, files in os.walk(self.plugin_dir):
            for f in files:
                if root != self.plugin_dir and (f.endswith('Plugin.py') or f.endswith('plugin.py')):

                    #create action and add it to mainwindow
                    path = os.path.join(root, f)
                    pAction = PluginAction(self, path)
                    self.pluginActions.append(pAction)
                    self.emit(SIGNAL('insertPluginAction(PyQt_PyObject)'), pAction)

        #activate all plugins which where active on previous program execution
        self.__getActivePlugins()

    def loadPlugin(self, path):
        """Load plugin from plugin folder. Name of class and file of plugin must be the same."""
        for i in range(self.pluginActions.__len__()):
            if self.pluginActions[i].path == path:
                #print path
                name = os.path.basename(path)[:-3]
                try:
                    self.plugins[path] = getattr(__import__('plugins.' + name), name)()
                except AttributeError:
                    Logger.getInstance().addLogMessage("PluginLoader", "Error while loading plugin " + name + ". Class " + name + " not found", Logger.MSG_TYPE_ERROR, True)
                try:
                    self.plugins[path].initPlugin(self.signalproxy)     # init plugin with signal interface
                except AttributeError:
                    Logger.getInstance().addLogMessage("PluginLoader", "Error while loading plugin " + name + ". Function initPlugin() not found", Logger.MSG_TYPE_ERROR, True)

    def unloadPlugin(self, path):
        '''Called when user unloads plugin from menu'''
        try:
            deInit = getattr(self.plugins[path], "deInitPlugin")
        except AttributeError:
            Logger.getInstance().addLogMessage("PluginLoader", "Error while unloading " + path + ". No deInitPlugin() function found", Logger.MSG_TYPE_ERROR, True)
        except KeyError:
            Logger.getInstance().addLogMessage("PluginLoader", "Error while unloading " + path + ". Plugin not active", Logger.MSG_TYPE_ERROR, True)
        else:
            deInit()
            self.plugins.__delitem__(path)

    def __getActivePlugins(self, xmlfile=None):
        '''
        Function checks xml and returns if plugin was active on previous program execution
        xmlfile: specifies alternative path to xml file with plugin information (default: plugins/plugins.xml)
        '''
        fname = self.xmlFile
        if xmlfile != None:
            fname = xmlfile
        if os.path.exists(fname):
            fileObject = QFile(fname)
            Xml = QDomDocument("xmldoc")
            Xml.clear()
            if (fileObject.open(QIODevice.ReadOnly) != False):
                Xml.setContent(fileObject.readAll())
                fileObject.close()

            rootNode = Xml.documentElement()
            nodeList = rootNode.elementsByTagName("plugin")

            for i in range(nodeList.length()):
                bpNode = nodeList.at(i).toElement()
                for a in self.pluginActions:
                    if a.path == str(bpNode.attribute("path")):
                        a.setChecked(bpNode.attribute("active") == "y")

    def savePluginInfo(self, xmlfile=None):
        '''
        write plugin info to xml (plugin active/inactive ...)
        xmlfile: specifies alternative path to xml file with plugin information (default: plugins/plugins.xml)
        '''
        #create xml
        Xml = QDomDocument("xmldoc")
        rootNode = Xml.createElement("SysCDbgActivePlugins")
        Xml.appendChild(rootNode)

        for i in range(self.pluginActions.__len__()):
            pluginNode = Xml.createElement("plugin")
            pluginNode.setAttribute("path", self.pluginActions[i].path)
            if self.pluginActions[i].isChecked():
                pluginNode.setAttribute("active", "y")
            else:
                pluginNode.setAttribute("active", "n")
            rootNode.appendChild(pluginNode)

        #create and write xml file
        fname = self.xmlFile
        if xmlfile != None:
            fname = xmlfile
            if fname.endswith(".xml") == False:
                fname += ".xml"

        fileObject = QFile(fname)
        fileObject.open(QIODevice.WriteOnly)
        fileObject.writeData(Xml.toString())
        fileObject.close()
