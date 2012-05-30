from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4 import QtGui
from PyQt4 import QtCore
from ctags_support import EntryList, EntryItem, Function
import os

from PyQt4.QtCore import QThread


class CTagsRunner(QThread):
    tagsFileAvailable = pyqtSignal()

    def __init__(self, tmpFile, parent=None):
        super(CTagsRunner, self).__init__(parent)
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

    def openEntry(self, index):
        x = self.model().itemFromIndex(index).data(EntryItem.ENTRYROLE)
        self.signalproxy.openFile(x.file_, x.lineNumber)

    def contextMenuEvent(self, e):
        index = self.currentIndex()
        if not index.isValid():
            return

        x = self.model().itemFromIndex(index).data(EntryItem.ENTRYROLE)
        if not isinstance(x, Function):
            return

        def addBreakpoint(breakpoint_controller, file_, line):
            def f():
                breakpoint_controller.insertBreakpoint(file_, line)
            return f

        menu = QtGui.QMenu()
        menu.addAction(QtGui.QIcon(":/icons/images/bp.png"), "Break on %s (%s:%s)" % (x.name, x.file_, x.lineNumber), addBreakpoint(self.signalproxy.distributedObjects.breakpointController, x.file_, x.lineNumber))
        menu.exec_(self.viewport().mapToGlobal(e.pos()))
        e.accept()


class NavigationPlugin(QtCore.QObject):
    ''' CTags-based navigation plugin Widget '''

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

        self.view = NavigationView(self.signalproxy)
        self.view.setModel(self.entrylist.model)
        self.dockwidget.setWidget(self.view)

        # add widget to mainwindow
        self.signalproxy.emitAddDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
        self.signalproxy.distributedObjects.debugController.executableOpened.connect(self.update)

        self.ctagsRunner = CTagsRunner("%s/tags%d" % (str(QtCore.QDir.tempPath()), os.getpid()))
        self.ctagsRunner.tagsFileAvailable.connect(self.tagsFileReady, Qt.QueuedConnection)

        # load the tags if the plugin was loaded after the executable
        self.update()

    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.dockwidget.close()
        self.signalproxy.removeDockWidget(self.dockwidget)

    def update(self):
        sources = self.signalproxy.distributedObjects.gdb_connector.getSources()
        if len(sources) > 0:
            self.ctagsRunner.oneshot(sources)

    def tagsFileReady(self):
        self.entrylist.readFromFile(self.ctagsRunner.tmpFile)
        os.remove(self.ctagsRunner.tmpFile)
