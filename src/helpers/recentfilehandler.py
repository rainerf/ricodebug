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

from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QAction
from os.path import exists
import logging

class OpenRecentFileAction(QAction):
    """ Class extends QAction to open a recently used file."""
    def __init__(self, parent, distributedObjects):
        QAction.__init__(self, parent)
        self.debugController = distributedObjects.debugController
        QObject.connect(self, SIGNAL('triggered()'), self.__open)

    def __open(self):
        ''' Open executable (file named like action). '''
        self.debugController.openExecutable(str(self.text()))


class RecentFileHandler():

    def __init__(self, parent, recentFilesMenu, distributedObjects):
        """Load recently used file names to menu actions.
            @param recentFileActionCont: list[sessionmanager.OpenRecentFileAction], actions of items in menu
            @param nrRecentFileActions: integer, number of recently used files listed in menu
            @param distributedObjects: distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        self.distributedObjects = distributedObjects
        self.debugController = distributedObjects.debugController
        self.recentFilesMenu = recentFilesMenu
        self.settings = self.debugController.settings
        self.nrRecentFiles = 5
        self.recentfiles = []

        # array with menu actions
        self.actions = []
        self.__makeActions(parent)
        self.__getRecentFiles()
        self.__loadRecentFiles()
        
    def addToRecentFiles(self, filename):
        """ Add new filename to self.recentfiles """
        #check if filename is already in recently used files
        for i in range(self.nrRecentFiles):
            if (i < len(self.recentfiles) and filename == self.recentfiles[i]):
                self.recentfiles.pop(i)
        #add file
        self.recentfiles.insert(0, filename)
        #refresh menu & store to configfile
        self.__storeRecentFiles()
        self.__loadRecentFiles()
            
    def __storeRecentFiles(self):
        """ store filelist to configfile """
        self.settings.beginWriteArray("RecentlyUsedFiles")
        for i in range(self.nrRecentFiles):
            self.settings.setArrayIndex(i)
            self.settings.setValue("Filename", self.recentfiles[i])
        self.settings.endArray()
        
    def __makeActions(self, parent):
        for i in range(self.nrRecentFiles):
            self.actions.append(OpenRecentFileAction(parent, self.distributedObjects))
            self.recentFilesMenu.addAction(self.actions[i])
        
    def __getRecentFiles(self):
        """ get filelist from configfile """
        self.settings.beginReadArray("RecentlyUsedFiles")
        for i in range(self.nrRecentFiles):
            self.settings.setArrayIndex(i)
            filename = self.settings.value("Filename").toString()
            duplicate = False 
            for j in range(len(self.recentfiles)):
                if (filename != "" and self.recentfiles[j] == filename):
                    logging.debug("file %s appears multiple times in configfile. fixed now" % filename)
                    self.recentfiles.append("")
                    duplicate = True
            if not duplicate:
                self.recentfiles.append(filename)
        self.settings.endArray()
        
    def __loadRecentFiles(self):
        """Load recently used files from self.recentfiles to the menu. """
        for action_index in range(self.nrRecentFiles):
            filename = self.recentfiles[action_index]
            if exists(filename):
                self.actions[action_index].setText(filename)
                self.actions[action_index].setVisible(True)
            else:
                self.actions[action_index].setVisible(False)
            
