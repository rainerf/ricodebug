from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from ctags_support import EntryList
import os

# plugin requirements:
#  - plugin must be a package inside folder "plugins"
#  - package must contain one file ending with "Plugin.py" (e.g. SamplePlugin.py)
#  - this file must contain a class named like the file (e.g. SamplePlugin)
#  - this class must implement the functions initPlugin(signalproxy) and deInitPlugin() to load/unload plugin
#
# The variable PluginName in the __init__.py file of each package may be used to define a name for the plugin

class NavigationPlugin(QtCore.QObject):
    ''' CTags-based navigation plugin Widget '''
    
    # ================================= 
    # functions called by pluginloader
    # ================================= 
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.dockwidget = None
        
    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""
        
        self.signalproxy = signalproxy
        self.entrylist = EntryList()

        # create and place DockWidget in mainwindow using signalproxy
        self.dockwidget = QtGui.QDockWidget(None)
        self.dockwidget.setObjectName("Navigation")
        self.dockwidget.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Navigation", None, QtGui.QApplication.UnicodeUTF8))
        
        self.view = QtGui.QTreeView()
        self.view.setModel(self.entrylist.model)
        self.dockwidget.setWidget(self.view)
        
        # add widget to mainwindow
        self.signalproxy.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
        QtCore.QObject.connect(self.signalproxy.distributedObjects.debug_controller, QtCore.SIGNAL('executableOpened'), self.update)
        QtCore.QObject.connect(self.view, QtCore.SIGNAL("doubleClicked(QModelIndex)"), self.viewDoubleClicked)
        
    def viewDoubleClicked(self, index):
            file_ = str(index.sibling(index.row(), 1).data().toString())
            line = index.sibling(index.row(), 2).data().toInt()[0]
            self.signalproxy.openFile(file_, line)
        
    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.dockwidget.close()
        self.signalproxy.removeDockWidget(self.dockwidget)
        
    def update(self):
        sources = self.signalproxy.distributedObjects.gdb_connector.getSources()
        tmpFile = "%s/tags%d" % (str(QtCore.QDir.tempPath()), os.getpid())
        os.system('ctags --fields=afmikKlnsStz -f %s %s' % (tmpFile, " ".join(sources)))
        self.entrylist.readFromFile(tmpFile)
        self.view.setModel(self.entrylist.model)

