'''
Created on Jun 21, 2011

@author: root
'''
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QAction
from os.path import exists

class OpenRecentFileAction(QAction):
    """ Class extends QAction to open a recently used file."""
    def __init__(self, parent):
        QAction.__init__(self, parent)
        QObject.connect(self, SIGNAL('triggered()'), self.__open)
         
    def __open(self):
        ''' Open executable (file named like action). '''
        self.emit(SIGNAL('executableOpened'), str(self.text()))
        
class RecentFileHandler():
    def __init__(self, recentFileActionCont, nrRecentFileActions, distributed_objects):
        """Load recently used file names to menu actions. 
            @param recentFileActionCont: list[sessionmanager.OpenRecentFileAction], actions of items in menu
            @param nrRecentFileActions: integer, number of recently used files listed in menu
            @param distributed_objects: distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        self.distributed_objects = distributed_objects
        self.debug_controller = distributed_objects.debug_controller
        self.breakpoint_controller = distributed_objects.breakpoint_controller
        self.watch_controller = distributed_objects.watch_controller
        self.settings = self.debug_controller.settings
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
            if (included == False):
                included = self.settings.value("Filename") == filename
        self.settings.endArray()
        
        if (included == False):
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
            i = self.nrRecentFiles-1
        action_index = 0
        
        for action_index in range(self.nrRecentFiles):
            self.settings.setArrayIndex(i)
            filename = self.settings.value("Filename").toString()
            if exists(filename):
                self.actions[action_index].setText(filename)
                self.actions[action_index].setVisible(True)
            else:
                self.actions[action_index].setVisible(False)
            i = i-1
            if i < 0:
                i = self.nrRecentFiles-1
        
        self.settings.endArray()  