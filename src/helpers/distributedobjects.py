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

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSettings

from controllers.debugcontroller import DebugController
from .signalproxy import SignalProxy
from controllers.editorcontroller import EditorController
from .gdbconnector import GdbConnector
from controllers.filelistcontroller import FileListController
from controllers.stackcontroller import StackController
from controllers.tracepointcontroller import TracepointController
from datagraph.datagraphcontroller import DataGraphController
from variables.variablepool import VariablePool
from .stlvectorparser import StlVectorParser
from controllers.tracepointwavecontroller import TracepointWaveController
from .sessionmanager import SessionManager
from helpers.actions import Actions
from helpers.configstore import ConfigStore
from views.watchview import WatchView
from controllers.variableviewtooltipcontroller import VariableViewToolTipController
from views.variableviewtooltip import VariableViewToolTip
from views.breakpointview import BreakpointView
from views.gdbioview import GdbIoView
from views.inferiorioview import InferiorIoView
from views.scriptview import ScriptView
from views.threadview import ThreadView
from models.threadmodel import ThreadModel
from views.mitraceview import MiTraceView
from helpers.icons import Icons
from models.stoppointmodel import StoppointModel
from models.watchmodel import WatchModel
from models.localsmodel import LocalsModel
from views.treeitemview import TreeItemView
from helpers import scriptenv
from helpers import tracer


class DistributedObjects:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

        tracer.setClassName(scriptenv.CLASSNAME)
        self.settings = QSettings("fh-hagenberg", "ricodebug")
        self.configStore = ConfigStore(self.settings)
        self.gdb_connector = GdbConnector()
        self.signalProxy = SignalProxy(self)
        self.debugController = DebugController(self)
        self.actions = Actions(self)
        self.sessionManager = SessionManager(self)

        self.breakpointModel, _ = self.buildModelAndView(StoppointModel, BreakpointView, "Breakpoints", Icons.bp)

        self.variablePool = VariablePool(self)
        self.editorController = EditorController(self, mainwindow.ui.editorView)
        scriptView = self.buildView(ScriptView, "Python Console", Icons.python)
        tracer.setCallback(scriptView.appendTranscript)

        self.filelistController = FileListController(self)
        self.stackController = StackController(self)

        self.threadModel, _ = self.buildModelAndView(ThreadModel, ThreadView, "Threads", Icons.thread)
        self.watchModel, _ = self.buildModelAndView(WatchModel, WatchView, "Watch", Icons.watch)
        self.buildModelAndView(LocalsModel, TreeItemView, "Locals", Icons.locals)

        self.toolTipController = VariableViewToolTipController(self, VariableViewToolTip(self, self.editorController.getView()))

        self.tracepointController = TracepointController(self)

        self.buildView(InferiorIoView, "Output", Icons.console)
        self.buildView(GdbIoView, "GDB Console")

        self.datagraphController = DataGraphController(self)
        self.stlvectorParser = StlVectorParser(self)
        self.tracepointwaveController = TracepointWaveController(self)

        self.miView = self.buildView(MiTraceView, "MI Trace")

        self.scriptEnv = scriptenv.ScriptEnv(self)

    def buildModelAndView(self, ModelCls, ViewCls, name, icon=None):
        view = self.buildView(ViewCls, name, icon)
        model = ModelCls(self)
        view.setModel(model)
        return model, view

    def buildView(self, ViewCls, name, icon=None):
        dw = self.mainwindow.insertDockWidget(None, name, Qt.BottomDockWidgetArea, True)
        if icon:
            dw.setWindowIcon(icon)
        view = ViewCls(self, dw)
        dw.setWidget(view)
        return view
