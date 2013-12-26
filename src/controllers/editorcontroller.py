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

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QFont
from helpers.configstore import ConfigSet, ConfigItem, Separator
from helpers.icons import Icons


class EditorConfig(ConfigSet):
    def __init__(self):
        ConfigSet.__init__(self, "Editor", "Editor Settings", Icons.vertical)
        self.font = ConfigItem(self, "Font", ("DejaVu Sans Mono", 10))
        Separator(self, None)
        self.backgroundColor = ConfigItem(self, "Background Color", "#ffffff")
        self.identifierColor = ConfigItem(self, "Identifier Color", "#000000")
        self.keywordColor = ConfigItem(self, "Keyword Color", "#00007f")
        self.commentColor = ConfigItem(self, "Comment Color", "#007f00")
        self.stringColor = ConfigItem(self, "String Color", "#7f007f")
        self.numberColor = ConfigItem(self, "Number Color", "#007f7f")
        self.preprocessorColor = ConfigItem(self, "Preprocessor Color", "#7f7f00")
        self.tooltipIndicatorColor = ConfigItem(self, "Tooltip Indicator Color", "#cccccc")
        Separator(self, None)
        self.highlightColor = ConfigItem(self, "Highlight Color", "#ffffa0")
        self.highlightingDuration = ConfigItem(self, "Duration of Highlighting (ms)", 1500)
        Separator(self, None)
        self.showWhiteSpaces = ConfigItem(self, "Show White Spaces", False)
        self.showIndentationGuides = ConfigItem(self, "Show Indentation Guides", False)
        self.tabWidth = ConfigItem(self, "Tab Width", 4)
        self.wrapLines = ConfigItem(self, "Wrap Lines", True)
        self.folding = ConfigItem(self, "Allow Folding", True)
        # self.font = ConfigItem(self, "Font", ('DejaVu Sans Mono', 10, False, True))
        Separator(self, None)
        self.useBreakpointOverlays = ConfigItem(self, "Use Breakpoint Overlays", True)


class EditorController(QObject):
    def __init__(self, distributedObjects, view):
        QObject.__init__(self)
        self.distributedObjects = distributedObjects

        self.__view = view
        view.init(distributedObjects)

        self.distributedObjects.signalProxy.inferiorStoppedNormally.connect(self.__view.targetStoppedNormally)
        self.distributedObjects.signalProxy.inferiorReceivedSignal.connect(self.__view.targetStoppedWithSignal)
        self.distributedObjects.signalProxy.inferiorHasExited.connect(self.__view.targetExited)
        self.distributedObjects.signalProxy.saveFile.connect(self.saveCurrentFile)
        self.distributedObjects.signalProxy.fileModified.connect(self.__view.setFileModified)

        self.config = EditorConfig()
        self.distributedObjects.configStore.registerConfigSet(self.config)

    def jumpToLine(self, filename, line):
        line = int(line) - 1
        self.__view.openFile(filename)
        editor = self.__view.openedFiles[filename]
        editor.showLine(line)
        editor.highlightLine(line)

    def addStackMarker(self, filename, line):
        line = int(line) - 1
        self.__view.openFile(filename)
        editor = self.__view.openedFiles[filename]
        editor.markerAdd(line, editor.MARGIN_MARKER_STACK)

    def delStackMarkers(self, filename):
        if self.__view.isOpen(filename):
            editor = self.__view.openedFiles[filename]
            editor.markerDeleteAll(editor.MARGIN_MARKER_STACK)

    def saveCurrentFile(self):
        self.__view.getCurrentOpenedFile().saveFile()

    def closeOpenedFiles(self):
        return self.__view.removeAllTabs()

    def getCursorPosition(self):
        file_ = self.__view.getCurrentOpenedFile()
        line, _ = file_.getCursorPosition()
        return (file_.filename, line+1)

    def getView(self):
        return self.__view