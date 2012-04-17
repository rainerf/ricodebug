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

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QAction
from os.path import exists


class OpenRecentFileAction(QAction):
    """ Class extends QAction to open a recently used file."""
    executableOpened = pyqtSignal('QString')

    def __init__(self, parent):
        QAction.__init__(self, parent)
        self.triggered.connect(self.__open)

    def __open(self):
        ''' Open executable (file named like action). '''
        self.executableOpened.emit(str(self.text()))


class RecentFileHandler():
    def __init__(self, recentFileActionCont, nrRecentFileActions, distributedObjects):
        """Load recently used file names to menu actions.
            @param recentFileActionCont: list[sessionmanager.OpenRecentFileAction], actions of items in menu
            @param nrRecentFileActions: integer, number of recently used files listed in menu
            @param distributedObjects: distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        self.distributedObjects = distributedObjects
        self.debugController = distributedObjects.debugController
        self.breakpointController = distributedObjects.breakpointController
        self.watchController = distributedObjects.watchController
        self.settings = self.debugController.settings
        self.nrRecentFiles = nrRecentFileActions

        # array with menu actions
        self.actions = recentFileActionCont
        self.__loadRecentFiles()

    def addToRecentFiles(self, filename):
        """ Add new filename to recently used files. """
        #check if filename is already in recently used files
        size = self.settings.beginReadArray("RecentlyUsedFiles")
        included = False
        for i in range(size):
            self.settings.setArrayIndex(i)
            if not included:
                included = self.settings.value("Filename") == filename
        self.settings.endArray()

        if not included:
            self.settings.beginWriteArray("RecentlyUsedFiles")
            #increase index with every entry
            index = self.settings.value("RecentlyUsedFileIndex").toInt()[0]
            index = (index + 1) % self.nrRecentFiles
            self.settings.setValue("RecentlyUsedFileIndex", index)

            #add file
            self.settings.setArrayIndex(index)
            self.settings.setValue("Filename", filename)
            self.settings.endArray()

            #refresh menu
            self.__loadRecentFiles()

    def __loadRecentFiles(self):
        """Load recently used files from qsettings file to the menu. """
        self.settings.beginReadArray("RecentlyUsedFiles")

        last_used_index = self.settings.value("RecentlyUsedFileIndex", -1).toInt()[0]
        i = last_used_index
        if i < 0:
            i = self.nrRecentFiles - 1
        action_index = 0

        for action_index in range(self.nrRecentFiles):
            self.settings.setArrayIndex(i)
            filename = self.settings.value("Filename").toString()
            if exists(filename):
                self.actions[action_index].setText(filename)
                self.actions[action_index].setVisible(True)
            else:
                self.actions[action_index].setVisible(False)
            i = i - 1
            if i < 0:
                i = self.nrRecentFiles - 1

        self.settings.endArray()

