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

class SysCSimCtxPlugin():
    
    # ================================= 
    # functions called by pluginloader
    # ================================= 
    def __init__(self):
        self.widget = None  
        
    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""
        
        self.signalproxy = signalproxy
        
        self.ctx = None
        
        self.curr_delta_cycles = 0
        self.curr_sim_time_ps = 0
        self.curr_process = ""
        self.curr_process_kind = ""
        self.elaboration_done = ""
        self.in_simulator_control = ""

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
        
        self.progress = QtGui.QProgressBar(self.w)
        self.progress.setMinimum(0)
        self.progress.setMaximum(2)
        self.progress.setValue(0)
        self.progress.setFormat("")
        self.gridLayout.addWidget(self.progress, 1, 0, 1, 3)
        
        self.label_3 = QtGui.QLabel(self.w)
        self.label_3.setText("Current Process:")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        
        self.lineEdit_3 = QtGui.QLineEdit(self.w)
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setText("")
        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 2)
        
        self.label_4 = QtGui.QLabel(self.w)
        self.label_4.setText("Current Process Kind:")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        
        self.lineEdit_4 = QtGui.QLineEdit(self.w)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setText("")
        self.gridLayout.addWidget(self.lineEdit_4, 3, 1, 1, 2)
        
        self.label = QtGui.QLabel(self.w)
        self.label.setText("Current Simulation Time:")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        
        self.lineEdit = QtGui.QLineEdit(self.w)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setText("0")
        self.gridLayout.addWidget(self.lineEdit, 4, 1, 1, 1)
        
        self.comboBox = QtGui.QComboBox(self.w)
        self.comboBox.addItem("ps")
        self.comboBox.addItem("ns")
        self.comboBox.addItem("us")
        self.comboBox.addItem("ms")
        self.comboBox.addItem("s")
        self.comboBox.setCurrentIndex(1)
        self.gridLayout.addWidget(self.comboBox,4, 2, 1, 1)
        
        self.label_2 = QtGui.QLabel(self.w)
        self.label_2.setText("Current Delta Cycle Count:")
        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 1)
        
        self.lineEdit_2 = QtGui.QLineEdit(self.w)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setText("0")
        self.gridLayout.addWidget(self.lineEdit_2, 5, 1, 1, 2)

        QtCore.QMetaObject.connectSlotsByName(self.w)
        
        self.widget = QtGui.QDockWidget("SystemC Simulation Context")
        self.widget.setObjectName("SysCSimCtx")
        self.widget.setWidget(self.w)

        self.signalproxy.addDockWidget(Qt.BottomDockWidgetArea, self.widget, True)
        
        QObject.connect(self.signalproxy, SIGNAL('inferiorHasStopped(PyQt_PyObject)'), self.update)
        QObject.connect(self.signalproxy, SIGNAL('inferiorHasExited(PyQt_PyObject)'), self.clear)
        QObject.connect(self.comboBox, SIGNAL('currentIndexChanged(QString)'), self.comboBoxIndexChanged)
        
    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.widget.close()
        self.signalproxy.removeDockWidget(self.widget)
        
    def clear(self):
        self.ctx = None
        
        self.curr_delta_cycles = 0
        self.curr_sim_time_ps = 0
        self.curr_process = ""
        self.curr_process_kind = ""
        self.elaboration_done = ""
        self.in_simulator_control = ""
        
        self.updateGui()
        
    def update(self):
        curr_sim_time_var = None
        curr_delta_count_var = None
        curr_process_var = None
        curr_process_kind_var = None
        elaboration_done_var = None
        in_simulator_control_var = None
        
        self.curr_sim_time_ps = 0
        self.curr_delta_cycles = 0
        
        sc_get_curr_simcontext = "sc_get_curr_simcontext()"
        
        if self.ctx is None:
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
            curr_sim_time_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_curr_time->m_value")
            curr_delta_count_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_delta_count")
            curr_process_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_curr_proc_info->process_handle->sc_core::sc_object::m_name")
            curr_process_kind_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_curr_proc_info->kind")
            elaboration_done_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_elaboration_done")
            in_simulator_control_var = self.signalproxy.gdbEvaluateExpression("((sc_core::sc_simcontext*)" + self.ctx + ")->m_in_simulator_control")
            
            self.label_img.hide()
            self.label_error.hide()
        else:
            self.label_img.show()
            self.label_error.show()
                
        if curr_sim_time_var is not None:
            self.curr_sim_time_ps = int(curr_sim_time_var)
                
        if curr_delta_count_var is not None:
            self.curr_delta_cycles = int(curr_delta_count_var)
            
        if curr_process_var is not None:
            self.curr_process = str(self.parseName(str(curr_process_var)))
            
        if curr_process_kind_var is not None:
            self.curr_process_kind = str(curr_process_kind_var)
        
        if elaboration_done_var is not None:
            self.elaboration_done = str(elaboration_done_var)
        
        if in_simulator_control_var is not None:
            self.in_simulator_control = str(in_simulator_control_var)
        
        self.updateGui()
        
    def updateGui(self):
        self.comboBoxIndexChanged(self.comboBox.currentText())
        self.lineEdit_2.setText(str(self.curr_delta_cycles))
        self.lineEdit_3.setText(str(self.curr_process))
        self.lineEdit_4.setText(str(self.curr_process_kind))
        
        if self.elaboration_done == "false" and self.in_simulator_control == "false":
            self.progress.setValue(0)
            self.progress.setFormat("Elaboration")
        elif self.elaboration_done == "true" and self.in_simulator_control == "true":
            self.progress.setValue(1)
            self.progress.setFormat("Simulation")
        elif self.elaboration_done == "true" and self.in_simulator_control == "false":
            self.progress.setValue(2)
            self.progress.setFormat("Finished")
        else:
            self.progress.setValue(0)
            self.progress.setFormat("")
        
    def comboBoxIndexChanged(self, text):
        curr_sim_time = 0
        if text == "ps":
            curr_sim_time = self.curr_sim_time_ps
        elif text == "ns":
            curr_sim_time = self.curr_sim_time_ps * 1.0 / 1000
        elif text == "us":
            curr_sim_time = self.curr_sim_time_ps * 1.0 / 1000 / 1000
        elif text == "ms":
            curr_sim_time = self.curr_sim_time_ps * 1.0 / 1000 / 1000 / 1000
        elif text == "s":
            curr_sim_time = self.curr_sim_time_ps * 1.0 / 1000 / 1000 / 1000 / 1000
            
        self.lineEdit.setText(str(curr_sim_time))
    
    def parseName(self, name):
        r = re.search('(?<=\").*(?=\")', name)
        if r is not None:
            return r.group(0)
        else:
            return name

