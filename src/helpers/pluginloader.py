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
import logging


class PluginAction(QAction):
    """ Class extends QAction to load a plugin over a menu entry."""
    def __init__(self, parent, path):
        self.pluginldr = parent
        QAction.__init__(self, parent)

        self.classname = os.path.basename(path)[:-3]
        self.modulename = os.path.dirname(path)[os.path.dirname(path).rfind('/') + 1:]
        self.path = path

        self.setObjectName("actionPlugin" + os.path.basename(path)[:-3])
        self.setCheckable(True)
        self.setChecked(False)

        # import classname of plugin from __init__.py
        try:
            pluginmodule = __import__("plugins.%s" % self.modulename)
            module = getattr(pluginmodule, self.modulename)
            self.setText(module.PluginName)
        except ImportError:
            logging.error("No module named " + self.modulename + " found")
            raise
        except AttributeError:
            logging.error("Error finding name of plugin " + path + ". No PluginName function found")

            # if PluginName is not defined, name plugin like file
            self.setText(os.path.basename(path))

        #connect action to initPlugin() and deInitPlugin methods
        QObject.connect(self, SIGNAL('triggered(bool)'), self.__togglePlugin)

    def __togglePlugin(self, checked):
        ''' Load/Unload Plugin by toggling menu entries '''
        if checked:
            try:
                self.pluginldr.loadPlugin(self)
            except:
                self.setChecked(False)
        else:
            self.pluginldr.unloadPlugin(self)

    def setLoaded(self, loaded):
        self.setChecked(loaded)
        self.__togglePlugin(loaded)


class PluginLoader(QObject):
    '''PluginLoader.
        Goes through subfolders of /plugins and searches for plugin files(ending with "plugin.py").
        SamplePlugin provides a sample for such plugins.
    '''

    def __init__(self, distributedObjects):
        """CTOR of pluginloader."""
        QObject.__init__(self)
        self.plugin_dir = os.path.dirname(__file__) + '/../plugins'

        # contains the instances of the loaded modules' classes
        self.loadedPlugins = {}

        # all generated actions by their path
        self.pluginActions = {}

        # signalproxy for communication with plugins
        self.signalproxy = distributedObjects.signalProxy

        # xml file for plugin info
        self.xmlFile = self.plugin_dir + '/plugins.xml'

    def addAvailablePlugins(self):
        """Search in all subfolders of src/plugins for plugin files and add them as menu entries."""
        # go through subdirs of pluginfolder and identify pluginfiles (ending with "Plugins.py")
        for root, _, files in os.walk(self.plugin_dir):
            for f in files:
                if root != self.plugin_dir and (f.endswith('Plugin.py') or f.endswith('plugin.py')):

                    # create action and add it to mainwindow
                    path = os.path.join(root, f)
                    pAction = PluginAction(self, path)
                    self.pluginActions[path] = pAction
                    self.emit(SIGNAL('insertPluginAction(PyQt_PyObject)'), pAction)

        # activate all plugins which where active on previous program execution
        self.__getActivePlugins()

    def loadPlugin(self, plugin):
        """Load plugin from plugin folder. Name of class and file of plugin must be the same."""
        try:
            try:
                pluginmodule = __import__("plugins.%s.%s" % (plugin.modulename, plugin.classname))
                module = getattr(getattr(pluginmodule, plugin.modulename), plugin.classname)
                class_ = getattr(module, plugin.classname)

                self.loadedPlugins[plugin] = class_()
            except AttributeError:
                logging.error("Error while loading plugin " + plugin.modulename + ". Class " + plugin.classname + " not found")
            try:
                self.loadedPlugins[plugin].initPlugin(self.signalproxy)     # init plugin with signal interface
            except AttributeError:
                logging.error("Error while loading plugin " + plugin.classname + ". Function initPlugin() not found")
        except Exception as e:
            logging.error(e)
            raise

    def unloadPlugin(self, plugin):
        '''Called when user unloads plugin from menu'''
        try:
            self.loadedPlugins[plugin].deInitPlugin()
        except AttributeError:
            logging.error("Error while unloading " + plugin.modulename + ". No deInitPlugin() function found")
        except KeyError:
            # the plugin was not loaded, no need to fail
            pass
        else:
            del self.loadedPlugins[plugin]

    def __getActivePlugins(self):
        '''
        Function checks xml and returns if plugin was active on previous program execution
        xmlfile: specifies alternative path to xml file with plugin information
        '''
        if os.path.exists(self.xmlFile):
            fileObject = QFile(self.xmlFile)
            Xml = QDomDocument("xmldoc")
            Xml.clear()
            if (fileObject.open(QIODevice.ReadOnly)):
                Xml.setContent(fileObject.readAll())
                fileObject.close()

            rootNode = Xml.documentElement()
            nodeList = rootNode.elementsByTagName("plugin")

            for i in range(nodeList.length()):
                bpNode = nodeList.at(i).toElement()
                path = str(bpNode.attribute("path"))
                if path in self.pluginActions:
                    self.pluginActions[path].setLoaded(bpNode.attribute("active") == "y")
                else:
                    logging.warning("No plugin for %s found, maybe it was moved/deleted?", path)

    def savePluginInfo(self):
        '''
        write plugin info to xml (plugin active/inactive ...)
        xmlfile: specifies alternative path to xml file with plugin information
        '''
        # create xml
        Xml = QDomDocument("xmldoc")
        rootNode = Xml.createElement("SysCDbgActivePlugins")
        Xml.appendChild(rootNode)

        for i in self.pluginActions.itervalues():
            pluginNode = Xml.createElement("plugin")
            pluginNode.setAttribute("path", i.path)
            if i.isChecked():
                pluginNode.setAttribute("active", "y")
            else:
                pluginNode.setAttribute("active", "n")
            rootNode.appendChild(pluginNode)

        # create and write xml file
        fileObject = QFile(self.xmlFile)
        fileObject.open(QIODevice.WriteOnly)
        fileObject.writeData(Xml.toString())
        fileObject.close()
