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

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, SIGNAL, QPointF, QLineF, QRectF
from PyQt4 import QtGui
from operator import attrgetter


class TracepointWaveDelegate(QtGui.QItemDelegate):
    '''Delegate for painting waveform to table
        overwrites methods for waveform column
    '''
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = TracepointWaveGraphicsView()
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setScene(value)

    def setModelData(self, editor, model, index):
        value = editor
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        if index.column() == 1:
            value = index.model().data(index, Qt.DisplayRole)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
            value.scene().render(painter, QRectF(option.rect.x(), option.rect.y(), value.scene().sceneRect().width(), option.rect.height() - 5), value.scene().sceneRect(), Qt.IgnoreAspectRatio)
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        size = QtGui.QItemDelegate.sizeHint(self, option, index)
        if (index.column() == 1):
            size.setWidth(index.model().data(index, Qt.DisplayRole).scene().width)
        return size


class TracepointWaveGraphicsView(QtGui.QGraphicsView):
    '''QGraphicsView for wave'''
    def __init__(self, name):
        '''CTOR
           @param name: string, shown as name of variable
        '''
        QtGui.QGraphicsView.__init__(self)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.name = name

    def getName(self):
        return self.name


class TracepointWaveScene(QtGui.QGraphicsScene):
    '''QGraphicsView for wave'''
    def __init__(self, type_, values, duration):
        '''CTOR
           @param type_: string, must be in supported types
           @param values: list of values of variable
           @param duration: integer, holds stepwidth of wave
        '''
        QtGui.QGraphicsScene.__init__(self)
        self.supportedTypes = ["bool", "int", "float", "double"]
        self.vSpace = 10
        self.values = []
        self.curPos = QPointF(0, 2)
        self.type = type_
        self.width = duration
        self.valFont = QtGui.QFont("Arial", 7)
        self.valFontColor = QtGui.QColor()
        self.valFontColor.setGreen(100)
        self.setSceneRect(0, 0, self.width, 15)

        for v in values:
            self.appendValue(v, duration)

    def getSupportedTypes(self):
        ''' Returns supported waveform types
            @return list[string]
        '''
        return self.supportedTypes

    def getType(self):
        ''' @return string identifying type of TracepointWaveScene'''
        return self.type

    def appendValue(self, value, duration):
        ''' Append value to wave
            @param value: value to add
            @param duration: integer, defines duration(length) of value in wave
        '''
        drawEdge = len(self.values) > 0 and self.values[len(self.values) - 1] != value
        if drawEdge == True:
            self.__drawEdge()

        self.values.append(value)
        self.__drawLine(value, duration, drawEdge or len(self.values) == 1)
        self.setSceneRect(0, 0, self.width, 15)

    def __drawEdge(self):
        ''' Draws an edge depending on the type of the waveform. '''
        if self.type == "bool":
            self.addItem(QtGui.QGraphicsLineItem(QLineF(self.curPos, QPointF(self.curPos.x(), self.curPos.y() + self.vSpace))))
        elif self.type in self.supportedTypes:
            self.addItem(QtGui.QGraphicsLineItem(QLineF(self.curPos, QPointF(self.curPos.x() + 2, self.curPos.y() + self.vSpace))))
            self.addItem(QtGui.QGraphicsLineItem(QLineF(QPointF(self.curPos.x() + 2, self.curPos.y()), QPointF(self.curPos.x(), self.curPos.y() + self.vSpace))))

    def __drawLine(self, value, duration, printvalue=True):
        ''' Draws a line depending on the type of the waveform.
            @param value: value to add to wave
            @param duration: integer, defines duration(length) of value in wave
            @param printvalue: bool, add values to waveform (for value-type waveforms only)
        '''
        self.width = self.width + duration
        tmp = self.curPos
        self.curPos = QPointF(self.curPos.x() + duration, self.curPos.y())
        if self.type == "bool":
            if value == True:
                self.addItem(QtGui.QGraphicsLineItem(QLineF(tmp, self.curPos)))
            else:
                self.addItem(QtGui.QGraphicsLineItem(tmp.x(), tmp.y() + self.vSpace, self.curPos.x(), self.curPos.y() + self.vSpace))
        elif self.type in self.supportedTypes:
            if printvalue == True:
                text = QtGui.QGraphicsTextItem(str(value))
                text.setFont(self.valFont)
                text.setDefaultTextColor(self.valFontColor)
                text.setPos(QPointF(tmp.x() + 4, tmp.y() - 5))
                self.addItem(text)

            self.addItem(QtGui.QGraphicsLineItem(QLineF(tmp, self.curPos)))
            self.addItem(QtGui.QGraphicsLineItem(tmp.x(), tmp.y() + self.vSpace, self.curPos.x(), self.curPos.y() + self.vSpace))


class TracepointWaveModel(QAbstractTableModel):
    '''TableModel for TracepointWaveView.
        Holds a list of TracepointWaveGraphicsViews.
        Every TracepointWaveGraphicsView holds a TracepointWaveScene which represents a waveform.
    '''
    def __init__(self):
        QAbstractTableModel.__init__(self)

        # each TracepointWaveGraphicsView in list holds one TracepointWaveScene
        self.waveforms = []

        # factor for zoom in/out functions
        self.zoomfactor = 1.05

        # stepwidth in waveform
        self.duration = 30

        # const column of waveform
        self.wavecolumn = 1

    def cleanUp(self, resetzoomvalue=True):
        '''Remove all waveforms and reset model'''
        while self.rowCount(parent=None) > 0:
            idx = len(self.waveforms) - 1
            self.beginRemoveRows(QModelIndex(), idx, idx)
            self.waveforms.pop()
            self.endRemoveRows()

        self.waveforms = []
        if resetzoomvalue:
            self.duration = 30

    def updateTracepointWave(self, name, type_, value):
        '''Update existing tracepoint wave. If model does not contain a wave with given name and type a new wave is created.
            @param name: string, name of wave in tableview
            @param type_: string, type of wave (must be supported by TracepointWaveScene)
            @param value: value to append to wave
        '''
        i = self.__getTracepointWaveIndex(name, type_)

        if i != None:
            #append value to existing wave
            wave = self.data(i, Qt.EditRole)
            wave.scene().appendValue(value, self.duration)
            self.setData(i, wave)
        else:
            #insert new wave
            waveform = TracepointWaveGraphicsView(name)
            waveform.setScene(TracepointWaveScene(type_, [value], self.duration))

            self.beginInsertRows(QModelIndex(), len(self.waveforms), len(self.waveforms))
            self.waveforms.append(waveform)
            self.endInsertRows()

    def __getTracepointWaveIndex(self, name, type_):
        for i in range(len(self.waveforms)):
            if self.waveforms[i].getName() == name and self.waveforms[i].scene().getType() == type_:
                return self.createIndex(i, self.wavecolumn, None)
        return None

    def zoomIn(self):
        '''Zoom wave horizontally'''
        self.duration = self.duration * self.zoomfactor
        for i in range(len(self.waveforms)):
            prevScene = self.waveforms[i].scene()
            waveform = TracepointWaveGraphicsView(self.waveforms[i].name)
            waveform.setScene(TracepointWaveScene(prevScene.type, prevScene.values, self.duration))
            self.waveforms[i] = waveform
            index = self.createIndex(i, self.wavecolumn, None)
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def zoomOut(self):
        '''Zoom wave horizontally'''
        self.duration = self.duration / self.zoomfactor
        for i in range(len(self.waveforms)):
            prevScene = self.waveforms[i].scene()
            waveform = TracepointWaveGraphicsView(self.waveforms[i].name)
            waveform.setScene(TracepointWaveScene(prevScene.type, prevScene.values, self.duration))
            self.waveforms[i] = waveform
            index = self.createIndex(i, self.wavecolumn, None)
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def rowCount(self, parent):
        return len(self.waveforms)

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        ret = None
        if(index.row() < len(self.waveforms)):
            wave = self.waveforms[index.row()]
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    ret = wave.getName()
                elif index.column() == self.wavecolumn:
                    ret = wave
            elif role == Qt.EditRole:
                if index.column() == self.wavecolumn:
                    ret = wave
        return ret

    def sort(self, column, order):
        if order == Qt.AscendingOrder:
            rev = False
        else:
            rev = True

        if column == 0:
            key = 'name'
            self.beginResetModel()
            self.waveforms.sort(key=attrgetter(key), reverse=rev)
            self.endResetModel()
            self.emit(SIGNAL("orderChanged()"))

    def headerData(self, section, orientation, role):
        ret = None
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    ret = "Variable"
                if section == self.wavecolumn:
                    ret = "Wave"
        return ret
