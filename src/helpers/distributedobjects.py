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

from controllers.debugcontroller import DebugController
from .signalproxy import SignalProxy
from controllers.editorcontroller import EditorController
from .gdbconnector import GdbConnector
from controllers.filelistcontroller import FileListController
from controllers.stackcontroller import StackController
from controllers.localscontroller import LocalsController
from controllers.tracepointcontroller import TracepointController
from controllers.watchcontroller import WatchController
from datagraph.datagraphcontroller import DataGraphController
from variables.variablepool import VariablePool
from .stlvectorparser import StlVectorParser
from controllers.tracepointwavecontroller import TracepointWaveController
from .sessionmanager import SessionManager
from helpers.actions import Actions
from helpers.configstore import ConfigStore
from PyQt4.QtCore import QSettings
from views.watchview import WatchView
from views.localsview import LocalsView
from controllers.tooltipcontroller import ToolTipController
from views.tooltipview import ToolTipView
from views.breakpointview import BreakpointView
from views.gdbioview import GdbIoView
from views.inferiorioview import InferiorIoView
from views.pyioview import PyIoView
from views.threadview import ThreadView
from models.threadmodel import ThreadModel
from views.mitraceview import MiTraceView
from helpers.icons import Icons
from models.stoppointmodel import StoppointModel


class DistributedObjects:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.settings = QSettings("fh-hagenberg", "ricodebug")
        self.configStore = ConfigStore(self.settings)
        self.gdb_connector = GdbConnector()
        self.actions = Actions()
        self.signalProxy = SignalProxy(self)
        self.sessionManager = SessionManager(self)

        self.breakpointModel, _ = self.buildModelAndView(StoppointModel, BreakpointView, "Breakpoints", Icons.bp)

        self.debugController = DebugController(self)
        self.variablePool = VariablePool(self)
        self.editorController = EditorController(self)
        self.toolTipController = ToolTipController(self, ToolTipView(self, self.editorController.editor_view))
        self.filelistController = FileListController(self)
        self.stackController = StackController(self)

        self.threadModel, _ = self.buildModelAndView(ThreadModel, ThreadView, "Threads", Icons.thread)

        self.watchView = WatchView()
        self.watchController = WatchController(self, self.watchView)

        self.localsView = LocalsView()
        self.localsController = LocalsController(self, self.localsView)

        self.tracepointController = TracepointController(self)

        self.buildView(PyIoView, "Python Console", Icons.python)
        self.buildView(InferiorIoView, "Output", Icons.console)
        self.buildView(GdbIoView, "GDB Console")

        self.datagraphController = DataGraphController(self)
        self.stlvectorParser = StlVectorParser(self)
        self.tracepointwaveController = TracepointWaveController(self)

        self.miView = self.buildView(MiTraceView, "MI Trace")

    def buildModelAndView(self, ModelCls, ViewCls, name, icon=None):
        view = self.buildView(ViewCls, name, icon)
        model = ModelCls(self)
        view.setModel(model)
        return model, view

    def buildView(self, ViewCls, name, icon=None):
        dw = self.mainwindow.newDockWidget(name, Qt.BottomDockWidgetArea, True)
        if icon:
            dw.setWindowIcon(icon)
        view = ViewCls(self, dw)
        dw.setWidget(view)
        return view
