# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphes and SystemC features.
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

import re
from PyQt4.QtCore import Qt, QObject, SIGNAL
from PyQt4 import QtCore, QtGui

# plugin requirements:
#  - plugin must be a package inside folder "plugins"
#  - package must contain one file ending with "Plugin.py" (e.g. SamplePlugin.py)
#  - this file must contain a class named like the file (e.g. SamplePlugin)
#  - this class must implement the functions initPlugin(signalproxy) and deInitPlugin() to load/unload plugin
#
# The variable PluginName in the __init__.py file of each package may be used to define a name for the plugin

class SysCModulesPlugin():
    
    # ================================= 
    # functions called by pluginloader
    # ================================= 
    def __init__(self):
        self.widget = None  
        
    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""
        
        self.signalproxy = signalproxy
        
        self.ctx = None
        self.loaded = False
        self.objects = []

        # create and place DockWidget in mainwindow using signalproxy
        self.w = QtGui.QWidget()
        
        self.gridLayout = QtGui.QGridLayout(self.w)
        
        self.label_img = QtGui.QLabel(self.w)
        self.label_img.setPixmap(QtGui.QPixmap(":/icons/images/important.png"))
        self.gridLayout.addWidget(self.label_img, 0, 0, 1, 1)
        self.label_img.hide()
        
        self.label_error = QtGui.QLabel(self.w)
        self.label_error.setText("No SystemC simulation context found!")
        self.gridLayout.addWidget(self.label_error, 0, 1, 1, 1)
        self.label_error.hide()
        
        self.view = QtGui.QTreeWidget(self.w)
        self.view.setColumnCount(2)
        self.viewHeaders = QtCore.QStringList()
        self.viewHeaders.append("Objects")
        self.viewHeaders.append("Types")
        self.view.setHeaderLabels(self.viewHeaders)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 2)

        QtCore.QMetaObject.connectSlotsByName(self.w)
        
        self.widget = QtGui.QDockWidget("SystemC Module Hierarchy")
        self.widget.setObjectName("SysCModules")
        self.widget.setWidget(self.w)

        self.signalproxy.addDockWidget(Qt.BottomDockWidgetArea, self.widget, True)
        
        QObject.connect(self.signalproxy, SIGNAL('inferiorStoppedNormally(PyQt_PyObject)'), self.update)
        QObject.connect(self.signalproxy, SIGNAL('inferiorHasExited(PyQt_PyObject)'), self.clear)
        QObject.connect(self.view, SIGNAL('expanded(QModelIndex)'), self.resizeColumn)
        
    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.widget.close()
        self.signalproxy.removeDockWidget(self.widget)
        
    def clear(self):
        self.ctx = None
        self.loaded = False
        self.objects = []
        
        self.updateGui()
        
    def update(self):
        if self.ctx is None:
            sc_get_curr_simcontext = "sc_get_curr_simcontext()"
            self.ctx = self.signalproxy.gdbEvaluateExpression(sc_get_curr_simcontext)
            if self.ctx is None:
                frame = 0
                depth = self.signalproxy.gdbGetStackDepth()
                if depth is not None:
                    while ((self.ctx is None) and (frame < (depth-2))):
                        frame = frame + 1
                        self.signalproxy.gdbSelectStackFrame(frame)
                        self.ctx = self.signalproxy.gdbEvaluateExpression(sc_get_curr_simcontext)
        
                self.signalproxy.gdbSelectStackFrame(0)
        
        if self.ctx is not None:
            self.label_img.hide()
            self.label_error.hide()
        else:
            self.objects = []
            self.updateGui()
            self.label_img.show()
            self.label_error.show()
            
        if self.loaded:
            return
        
        content = None
        elaboration_done = None
        if self.ctx is not None:
            elaboration_done = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_elaboration_done")
            content = self.signalproxy.getStlVectorContent("((sc_core::sc_simcontext*)" + self.ctx + ")->m_module_registry->m_module_vec")
                
        if elaboration_done == "true" and content is not None:
            self.loaded = True
            self.objects = []
            for item in content:
                name = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_module**)" + item + "))->m_name")
                parent = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_module**)" + item + "))->m_parent")
                if parent != "0x0":
                    parent = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_module**)" + item + "))->m_parent->m_name")
                else:
                    parent = None
                    
                kind = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_module**)" + item + "))->kind()")
                if name is not None:
                    self.objects.append((str(name), str(parent), str(kind)))
                    
                    children = self.signalproxy.getStlVectorContent("(*((sc_core::sc_module**)" + item + "))->m_child_objects")
                    if children is not None:
                        for child in children:
                            childKind = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_object**)" + child + "))->kind()")
                            childName = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_object**)" + child + "))->m_name")
                            childParent = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_object**)" + child + "))->m_parent")
                            if childParent != "0x0":
                                childParent = self.signalproxy.gdbEvaluateExpression("(*((sc_core::sc_object**)" + child + "))->m_parent->m_name")
                            else:
                                childParent = None
                            
                            if childName is not None and str(self.parseName(childKind)) != "sc_module":
                                self.objects.append((str(childName), str(childParent), str(childKind)))
        
        self.updateGui()
        
    def updateGui(self):
        self.view.clear()
        self.treeItems = {}
        
        for object in self.objects:
            if object[1] == "None":
                self.treeItems[str(object[0])] = QtGui.QTreeWidgetItem(self.view)
            else:
                self.treeItems[str(object[0])] = QtGui.QTreeWidgetItem(self.treeItems[str(object[1])])
                
            self.treeItems[str(object[0])].setText(0, str(self.parseName(object[0])))
            self.treeItems[str(object[0])].setText(1, str(self.parseName(object[2])))
            
            if str(self.parseName(object[2])) == "sc_module":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_module.png")))
            elif str(self.parseName(object[2])) == "sc_method_process" or str(self.parseName(object[2])) == "sc_thread_process" or str(self.parseName(object[2])) == "sc_cthread_process":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_process.png")))
            elif str(self.parseName(object[2])) == "sc_signal":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_signal.png")))
            elif str(self.parseName(object[2])) == "sc_port":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_port.png")))
            elif str(self.parseName(object[2])) == "sc_in":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_in.png")))
            elif str(self.parseName(object[2])) == "sc_out":
                self.treeItems[str(object[0])].setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/icons/images/sc_out.png")))
            
    def parseName(self, name):
        r = re.search('(?<=\.)\w*(?=\")', name)
        if r is not None:
            return r.group(0)
        else:
            r = re.search('(?<=\")\w*(?=\")', name)
            if r is not None:
                return r.group(0)
            else:
                return name
            
    def resizeColumn(self, index):
        """Resize the first column to contents when expanded."""
        self.view.resizeColumnToContents(0)

