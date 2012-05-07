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

from PyQt4.QtCore import QObject, Qt, SIGNAL
from models.tracepointwavemodel import TracepointWaveModel, TracepointWaveDelegate
from views.tracepointwaveview import TracepointWaveView
import logging


class TracepointWaveController(QObject):
    '''Controller for Tracepoint Wave widget.
        Following datatypes can be displayed in waveform: bool, int, float, double
    '''

    def __init__(self, distributedObjects):
        '''CTOR'''
        QObject.__init__(self)

        self.distributedObjects = distributedObjects
        self.model = TracepointWaveModel()
        self.supportedTypes = ["bool", "int", "float", "double"]
        self.view = TracepointWaveView()
        self.view.setModel(self.model)
        delegate = TracepointWaveDelegate()

        # TracepointWaveView using TracepointWaveDelegate to paint waveforms
        self.view.setItemDelegate(delegate)
        QObject.connect(self.view.getZoomInButton(), SIGNAL("clicked()"), self.zoomIn)
        QObject.connect(self.view.getZoomOutButton(), SIGNAL("clicked()"), self.zoomOut)
        QObject.connect(self.distributedObjects.signalProxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        QObject.connect(self.distributedObjects.signalProxy, SIGNAL('cleanupModels()'), self.model.cleanUp)

    def insertDockWidgets(self):
        '''Function invoked when mainwindow allows controllers to insert widgets'''
        self.distributedObjects.signalProxy.emitAddDockWidget(Qt.BottomDockWidgetArea, self.view.getDockWidget(), True)

    def updateTracepointWaveView(self, list_):
        ''' Repaint tracepoint waves
            @param list_: list of ValueList objects
        '''
        self.model.cleanUp(False)    # clean up without reseting zoom
        for item in list_:
            for v in item.values:
                self.__updateTracepointWave(item.name, item.type, v)

    def zoomIn(self):
        '''Zoom wave horizontally'''
        self.model.zoomIn()
        self.view.resizeColumnsToContents()

    def zoomOut(self):
        '''Zoom wave horizontally'''
        self.model.zoomOut()
        self.view.resizeColumnsToContents()

    def __updateTracepointWave(self, name, type_, value):
        ''' Append value to tracepoint wave. Creates new wave if model does not contain wave with name and value type
            @param name: string with variable name
            @param type_: string with type of variable ("bool", "int", "float", "double" supported).
            @param value: value of variable
        '''
        if type_ in self.supportedTypes:
            self.model.updateTracepointWave(name, type_, value)
            self.view.resizeColumnsToContents()
        else:
            logging.error("Could not update tracepoint wave. Illegal variable type.")
