from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4 import QtGui
from PyQt4 import QtCore
from ctags_support import EntryModel
import os

from PyQt4.QtCore import QThread
from helpers.modeltest import ModelTest
from helpers.configstore import ConfigSet, ConfigItem
from plugins.Navigation.ctags_support import Entry
from helpers.icons import Icons


class CTagsRunner(QThread):
    tagsFileAvailable = pyqtSignal()

    def __init__(self, tmpFile, parent=None):
        QThread.__init__(self, parent)
        self.tmpFile = tmpFile
        self.sources = None

    def oneshot(self, sources):
        self.sources = sources
        self.start()

    def run(self):
        os.system('ctags --fields=afmikKlnsStz -f %s %s' % (self.tmpFile, " ".join(self.sources)))
        self.tagsFileAvailable.emit()


class NavigationView(QtGui.QTreeView):
    def __init__(self, signalproxy, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        self.signalproxy = signalproxy
        self.doubleClicked.connect(self.openEntry)
        self.setHeaderHidden(True)

    def openEntry(self, index):
        x = self.model().data(index, EntryModel.InternalDataRole)
        self.signalproxy.openFile(x.file, x.line)
        pass

    def contextMenuEvent(self, e):
        index = self.currentIndex()
        if not index.isValid():
            return

        x = self.model().data(index, EntryModel.InternalDataRole)
        if not x.type_ == Entry.FUNCTION:
            return

        def addBreakpoint(file_, line):
            def f():
                self.signalproxy.distributedObjects.breakpointModel.insertBreakpoint(file_, line)
            return f

        menu = QtGui.QMenu()
        menu.addAction(Icons.bp, "Break on %s (%s:%s)" % (x.name, x.file, x.line), addBreakpoint(x.file, x.line))
        menu.exec_(self.viewport().mapToGlobal(e.pos()))
        e.accept()


class NavigationPluginConfig(ConfigSet):
    def __init__(self):
        ConfigSet.__init__(self, "Navigation Plugin", "Navigation Plugin Settings")
        self.groupByFiles = ConfigItem(self, "Group by Files", True)
        self.ignorePaths = ConfigItem(self, "Ignore Files in Paths", "/usr:/opt")


class NavigationPlugin(QtCore.QObject):
    ''' CTags-based navigation plugin Widget '''

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.dockwidget = None

    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""

        self.signalproxy = signalproxy
        self.model = EntryModel()

        self.config = NavigationPluginConfig()
        signalproxy.distributedObjects.configStore.registerConfigSet(self.config)
        self.config.itemsHaveChanged.connect(self.update)

        self.view = NavigationView(self.signalproxy)
        self.view.setModel(self.model)

        # create and place DockWidget in mainwindow using signalproxy
        self.signalproxy.insertDockWidget(self, self.view, "Navigation", Qt.BottomDockWidgetArea, True)

        self.signalproxy.distributedObjects.debugController.executableOpened.connect(self.update)

        self.ctagsRunner = CTagsRunner("%s/tags%d" % (str(QtCore.QDir.tempPath()), os.getpid()))
        self.ctagsRunner.tagsFileAvailable.connect(self.tagsFileReady, Qt.QueuedConnection)

        # load the tags if the plugin was loaded after the executable
        self.update()

    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.signalproxy.removeDockWidget(self)

    def update(self):
        self.model.clear()
        sources = self.signalproxy.distributedObjects.gdb_connector.getSources()
        if len(sources) > 0:
            self.ctagsRunner.oneshot(sources)

    def tagsFileReady(self):
        self.model.readFromFile(self.ctagsRunner.tmpFile, self.config.groupByFiles.value, self.config.ignorePaths.value.split(":"))
        os.remove(self.ctagsRunner.tmpFile)
