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

from controllers.debugcontroller import DebugController
from signalproxy import SignalProxy
from controllers.editorcontroller import EditorController
from gdbconnector import GdbConnector
from controllers.filelistcontroller import FileListController
from controllers.stackcontroller import StackController
from controllers.localscontroller import LocalsController
from controllers.breakpointcontroller import BreakpointController
from controllers.tracepointcontroller import TracepointController
from controllers.watchcontroller import WatchController
from controllers.pyiocontroller import PyIoController
from controllers.inferioriocontroller import InferiorIoController
from controllers.gdbiocontroller import GdbIoController
from datagraph.datagraphcontroller import DataGraphController
from variables.variablepool import VariablePool
from actions import Actions
from stlvectorparser import StlVectorParser
from controllers.tracepointwavecontroller import TracepointWaveController
from sessionmanager import SessionManager


class DistributedObjects:
    def __init__(self):
        self.gdb_connector = GdbConnector()
        self.actions = Actions()
        self.signalProxy = SignalProxy(self)
        self.sessionManager = SessionManager(self)
        self.editorController = EditorController(self)
        self.breakpointController = BreakpointController(self)
        self.debugController = DebugController(self)
        self.variablePool = VariablePool(self)
        self.filelistController = FileListController(self)
        self.stackController = StackController(self)
        self.watchController = WatchController(self)
        self.localsController = LocalsController(self)
        self.tracepointController = TracepointController(self)
        self.pyioController = PyIoController(self)
        self.inferiorioController = InferiorIoController(self)
        self.gdbioController = GdbIoController(self)
        self.datagraphController = DataGraphController(self)
        self.stlvectorParser = StlVectorParser(self)
        self.tracepointwaveController = TracepointWaveController(self)
