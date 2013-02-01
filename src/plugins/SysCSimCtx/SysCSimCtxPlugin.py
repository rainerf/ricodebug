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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon, QLabel
from PyQt4 import QtGui
from helpers.tools import cpp2py
import ui_syscsimctxwidget


class SysCSimCtxPlugin:
    class SbInfo:
        def __init__(self):
            self.time = None
            self.process = None

        def __str__(self):
            v = []
            if self.time:
                v.append(self.time)
            if self.process:
                v.append("in %s" % self.process)

            if v:
                return ", ".join(v)
            else:
                return "(no information)"

    def initPlugin(self, signalproxy):
        self.ctxFound = False

        self.__sp = signalproxy

        self.w = QtGui.QWidget()
        self.ui = ui_syscsimctxwidget.Ui_SysCSimCtxWidget()
        self.ui.setupUi(self.w)

        self.ui.progress.setMinimum(0)
        self.ui.progress.setMaximum(2)
        self.ui.progress.setFormat("")

        self.ui.simTimeCB.addItems(["ps", "ns", "us", "ms", "s"])
        self.ui.simTimeCB.setCurrentIndex(1)
        self.ui.simTimeCB.currentIndexChanged.connect(self._setSimTime)

        self.ui.writeCheckBox.setEnabled(False)

        self.ui.warningIcon.setPixmap(QIcon.fromTheme("dialog-warning").pixmap(32, 32))

        self.__sp.inferiorStoppedNormally.connect(self._findSimVariables)
        self.__sp.inferiorHasExited.connect(self.clear)

        self.__sp.insertDockWidget(self, self.w, "SystemC Simulation Context", Qt.BottomDockWidgetArea, True)

        # statusbar widget
        self.sbLabel = QLabel()
        self.__sp.insertStatusbarWidget(self, self.sbLabel)

        self._currDeltaCycles = None
        self._currProcess = None
        self._currProcessHandle = None
        self._currProcessKind = None
        self._currSimTime = None
        self._elaborationDone = None
        self._inSimulatorControl = None
        self._writeCheck = None
        self._simContext = None

        self.clear()

        self._findSimVariables()

    def deInitPlugin(self):
        self.__sp.removeDockWidget(self)
        self.__sp.removeStatusbarWidget(self)
        self.clear()
        self.__sp.inferiorStoppedNormally.disconnect(self._findSimVariables)
        self.__sp.inferiorHasExited.disconnect(self.clear)

    def clear(self):
        self.ctxFound = False
        self._sbInfo = self.SbInfo()
        self.ui.progress.setFormat("")
        self.ui.progress.setValue(0)
        self.ui.processEdit.setText("")
        self.ui.processKindEdit.setText("")
        self.ui.simTimeEdit.setText("")
        self.ui.deltaCycleEdit.setText("")
        self.ui.writeCheckBox.setChecked(False)
        self.ui.stack.setCurrentIndex(1)

        for i in [self._currDeltaCycles, self._currProcess,
                  self._currProcessKind, self._currSimTime,
                  self._elaborationDone, self._inSimulatorControl,
                  self._writeCheck, self._simContext]:
            if i:
                i.die()

    def _findSimVariables(self):
        if self.ctxFound:
            return

        depth = self.__sp.gdbGetStackDepth()
        if depth is None:
            return

        frame = 0
        while not self.ctxFound and frame <= depth:
            self.__sp.gdbSelectStackFrame(frame)
            if self.__sp.gdbEvaluateExpression("sc_get_curr_simcontext()") is not None:
                self.ctxFound = True
                break
            frame += 1

        if self.ctxFound:
            self._simContext = self.__sp.distributedObjects.variablePool.getVar("sc_get_curr_simcontext()")["*"]

            self._currSimTime = self._simContext["m_curr_time"]["m_value"]
            self._currSimTime.changed.connect(self._setSimTime)
            self._setSimTime()

            self._currDeltaCycles = self._simContext["m_delta_count"]
            self._currDeltaCycles.changed.connect(self._setDeltaCycle)
            self._setDeltaCycle(self._currDeltaCycles.value)

            if self._simContext["m_curr_proc_info"]["process_handle"]["*"] is not None:
                self._currProcess = self._simContext["m_curr_proc_info"]\
                    ["process_handle"]["*"]["m_name"]
                self._currProcess.changed.connect(self._setProcess)
                self._setProcess(self._currProcess.value)
            else:
                self._currProcessHandle = \
                    self._simContext["m_curr_proc_info"]["process_handle"]
                self._currProcessHandle.changed.\
                    connect(self._changedProcessHandle)

            self._currProcessKind = self._simContext["m_curr_proc_info"]["kind"]
            self._currProcessKind.changed.connect(self._setProcessKind)
            self._setProcessKind(self._currProcessKind.value)

            self._elaborationDone = self._simContext["m_elaboration_done"]
            self._elaborationDone.changed.connect(self._setProgress)
            self._inSimulatorControl = self._simContext["m_in_simulator_control"]
            self._inSimulatorControl.changed.connect(self._setProgress)
            self._setProgress()

            self._writeCheck = self._simContext["m_write_check"]
            self._writeCheck.changed.connect(self._setWriteCheck)
            self._setWriteCheck(self._writeCheck.value)

            self.ui.stack.setCurrentIndex(0)

        self.__sp.gdbSelectStackFrame(0)

    def _setProgress(self):
        if not self._elaborationDone or not self._inSimulatorControl:
            return

        if not cpp2py(self._elaborationDone.value) and not cpp2py(self._inSimulatorControl.value):
            self.ui.progress.setValue(0)
            self.ui.progress.setFormat("Elaboration")
        elif cpp2py(self._elaborationDone.value) and cpp2py(self._inSimulatorControl.value):
            self.ui.progress.setValue(1)
            self.ui.progress.setFormat("Simulation")
        elif cpp2py(self._elaborationDone.value) and not cpp2py(self._inSimulatorControl.value):
            self.ui.progress.setValue(2)
            self.ui.progress.setFormat("Finished")
        else:
            self.ui.progress.setValue(0)
            self.ui.progress.setFormat("")

    def _setProcess(self, v):
        # process names are reported as '0x.... "name"', present only the name
        proc = str(v).split('"')[1]
        self.ui.processEdit.setText(proc)
        self._sbInfo.process = proc
        self._updateSbLabel()

    def _changedProcessHandle(self, v):
        if self._currProcess:
            self._currProcess.changed.disconnect()
            self._currProcess.die()
        self._currProcess = self.__sp.distributedObjects.variablePool.\
            getVar("(sc_core::sc_process_b *)" + str(v))["*"]["m_name"]
        self._currProcess.changed.connect(self._setProcess)
        self._setProcess(self._currProcess.value)

    def _setProcessKind(self, v):
        t = {
            "sc_core::SC_NO_PROC_": "No Process",
            "sc_core::SC_METHOD_PROC_": "Method",
            "sc_core::SC_THREAD_PROC_": "Thread",
            "sc_core::SC_CTHREAD_PROC_": "CThread",
        }

        self.ui.processKindEdit.setText(t[str(v)])

    def _setSimTime(self):
        if not self._currSimTime:
            return

        unit = str(self.ui.simTimeCB.currentText())
        time = float(self._currSimTime.value)

        div = {
            "ps": 0,
            "ns": 3,
            "us": 6,
            "ms": 9,
            "s": 12
        }

        time /= 10 ** div[unit]

        self.ui.simTimeEdit.setText("%g" % time)
        self._sbInfo.time = "%g %s" % (time, unit)
        self._updateSbLabel()

    def _setDeltaCycle(self, v):
        self.ui.deltaCycleEdit.setText(str(v))

    def _setWriteCheck(self, v):
        self.ui.writeCheckBox.setChecked(cpp2py(v))

    def _updateSbLabel(self):
        self.sbLabel.setText("<b>SystemC:</b> %s" % str(self._sbInfo))
