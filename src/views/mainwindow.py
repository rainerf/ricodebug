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

from PyQt4.QtGui import QMainWindow, QFileDialog, QLabel, QDockWidget, QPixmap
from PyQt4.QtCore import Qt, QObject
from ui_mainwindow import Ui_MainWindow
from helpers.distributedobjects import DistributedObjects
from helpers.recentfilehandler import OpenRecentFileAction, RecentFileHandler
from helpers.actions import Actions
from helpers.pluginloader import PluginLoader
from controllers.quickwatch import QuickWatch


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        """ init UI """
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionSaveSession.setEnabled(False)

        self.distributedObjects = DistributedObjects()

        self.debugController = self.distributedObjects.debugController
        self.settings = self.debugController.settings
        self.signalproxy = self.distributedObjects.signalProxy
        self.pluginloader = PluginLoader(self.distributedObjects)

        #init RecentFileHandler
        self.recentFileHandler = RecentFileHandler(self, self.ui.menuRecentlyUsedFiles, self.distributedObjects)
        self.debugController.executableOpened.connect(self.recentFileHandler.addToRecentFiles)

        # signal proxy
        self.signalproxy.inferiorIsRunning.connect(self.targetStartedRunning, Qt.QueuedConnection)
        self.signalproxy.inferiorStoppedNormally.connect(self.targetStopped, Qt.QueuedConnection) 
        self.signalproxy.inferiorReceivedSignal.connect(self.targetStopped, Qt.QueuedConnection)
        self.signalproxy.inferiorHasExited.connect(self.targetExited, Qt.QueuedConnection)

        self.signalproxy.addDockWidget.connect(self.addPluginDockWidget)
        self.signalproxy.removeDockWidget.connect(self.removeDockWidget)

        # Plugin Loader
        self.pluginloader.insertPluginAction.connect(self.addPluginAction)

        self.ui.actionSavePlugins.triggered.connect(self.showSavePluginsDialog)
        self.ui.actionLoadPlugins.triggered.connect(self.showLoadPluginsDialog)

        # Add editor to main window.
        self.ui.gridLayout.addWidget(self.distributedObjects.editorController.editor_view, 0, 0, 1, 1)

        self.pluginloader.addAvailablePlugins()

        # Tell everyone to insert their dock widgets into the main window
        self.signalproxy.emitInsertDockWidgets()

        # get filelist dockwidget
        self.filelist_dockwidget = self.findChild(QDockWidget, "FileListView")

        self.setWindowFilePath("<none>")
        self.setupUi()
        self.createInitialWindowPlacement()
        self.readSettings()

        self.quickwatch = QuickWatch(self, self.distributedObjects)

    def setupUi(self):
        self.__initActions()
        self.ui.statusLabel = QLabel()
        self.ui.statusLabel.setText("Not running")
        self.ui.statusbar.addPermanentWidget(self.ui.statusLabel)
        self.ui.statusIcon = QLabel()
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/inferior_not_running.png"))
        self.ui.statusbar.addPermanentWidget(self.ui.statusIcon)

    #def setupGraph(self):
        #self.scene = QGraphicsScene()
        #self.c2 = Composite()
        #self.c1 = Composite()
        #self.c1.addItem(LeafEntry("exp1", "val11"))
        #self.c1.addItem(LeafEntry("exp2 long", "val22"))
        #self.c2.addItem(LeafEntry("exp2 even longer", "val22"))
        #self.c2.addItem(CompositeEntry("subcomp", self.c1))
        #self.c2.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        #self.scene.addItem(self.c2)

    def __initActions(self):
        self.act = self.distributedObjects.actions
        # debug actions
        self.ui.menuDebug.addAction(self.act.actions[Actions.Run])
        self.ui.menuDebug.addAction(self.act.actions[Actions.Continue])
        self.ui.menuDebug.addAction(self.act.actions[Actions.Interrupt])
        self.ui.menuDebug.addAction(self.act.actions[Actions.Next])
        self.ui.menuDebug.addAction(self.act.actions[Actions.ReverseNext])
        self.ui.menuDebug.addAction(self.act.actions[Actions.Step])
        self.ui.menuDebug.addAction(self.act.actions[Actions.ReverseStep])
        self.ui.menuDebug.addAction(self.act.actions[Actions.Finish])
        self.ui.menuDebug.addAction(self.act.actions[Actions.RunToCursor])
        # file actions
        self.ui.menuFile.insertAction(self.ui.actionSaveSession, \
                self.act.actions[Actions.Open])
                
        self.act.actions[Actions.Open].setMenu(self.ui.menuRecentlyUsedFiles)
        self.ui.menuFile.addAction(self.act.actions[Actions.SaveFile])
        self.ui.menuFile.addAction(self.act.actions[Actions.Exit])

        # add them to menubar and also menuView to respect order
        self.ui.menubar.addAction(self.ui.menuFile.menuAction())
        self.ui.menubar.addAction(self.ui.menuView.menuAction())
        self.ui.menubar.addAction(self.ui.menuDebug.menuAction())
        self.ui.menubar.addAction(self.ui.menuHelp.menuAction())
        # now make toolbar actions
        self.ui.Main.addAction(self.act.actions[Actions.Open])
        self.ui.Main.addAction(self.act.actions[Actions.SaveFile])
        self.ui.Main.addSeparator()
        self.ui.Main.addAction(self.act.actions[Actions.Run])
        self.ui.Main.addAction(self.act.actions[Actions.Continue])
        self.ui.Main.addAction(self.act.actions[Actions.Interrupt])
        self.ui.Main.addAction(self.act.actions[Actions.Next])
        self.ui.Main.addAction(self.act.actions[Actions.Step])
        self.ui.Main.addAction(self.act.actions[Actions.Record])
        self.ui.Main.addAction(self.act.actions[Actions.ReverseNext])
        self.ui.Main.addAction(self.act.actions[Actions.ReverseStep])
        self.ui.Main.addAction(self.act.actions[Actions.Finish])
        self.ui.Main.addAction(self.act.actions[Actions.RunToCursor])
        self.ui.Main.addSeparator()
        self.ui.Main.addAction(self.act.actions[Actions.Exit])
        # connect actions
        self.__connectActions()

    def __connectActions(self):
        # file menu
        self.act.actions[Actions.Open].triggered.connect(self.showOpenExecutableDialog)
        self.act.actions[Actions.Exit].triggered.connect(self.close)
        self.act.actions[Actions.SaveFile].triggered.connect(self.signalproxy.emitSaveCurrentFile) 
        # debug menu

        self.act.actions[Actions.Run].triggered.connect(self.debugController.run)
        self.act.actions[Actions.Next].triggered.connect( self.debugController.next_)
        self.act.actions[Actions.Step].triggered.connect(self.debugController.step)
        self.act.actions[Actions.Continue].triggered.connect( self.debugController.cont)
        self.act.actions[Actions.Record].triggered.connect(self.debugController.toggle_record)
        self.act.actions[Actions.ReverseStep].triggered.connect(self.debugController.reverse_step)
        self.act.actions[Actions.ReverseNext].triggered.connect(self.debugController.reverse_next)

        self.act.actions[Actions.Interrupt].triggered.connect(self.debugController.interrupt)
        self.act.actions[Actions.Finish].triggered.connect( self.debugController.finish)
        self.act.actions[Actions.RunToCursor].triggered.connect(self.debugController.inferiorUntil) 
         
        self.ui.actionRestoreSession.triggered.connect(
                self.distributedObjects.sessionManager.showRestoreSessionDialog)
        self.ui.actionSaveSession.triggered.connect(
                self.distributedObjects.sessionManager.showSaveSessionDialog)

    def addPluginDockWidget(self, area, widget, addToggleViewAction):
        self.addDockWidget(area, widget)
        if addToggleViewAction:
            self.ui.menuShow_View.addAction(widget.toggleViewAction())

    def addPluginAction(self, Action):
        """ show plugin as menu entry """
        self.ui.menuPlugins.addAction(Action)

    def createInitialWindowPlacement(self):
        """
        Saves the window and widget placement after first start of program.
        """
        #check if settings do not exist
        initExists = self.settings.contains("InitialWindowPlacement/geometry")
        if not initExists:
            self.breakpointWidget = self.findChild(QDockWidget, "BreakpointView")
            self.fileListWidget = self.findChild(QDockWidget, "FileListView")
            self.dataGraphWidget = self.findChild(QDockWidget, "DataGraphView")
            self.watchWidget = self.findChild(QDockWidget, "WatchView")
            self.localsWidget = self.findChild(QDockWidget, "LocalsView")
            self.stackWidget = self.findChild(QDockWidget, "StackView")
            self.tracepointWidget = self.findChild(QDockWidget, "TracepointView")
            self.gdbIoWidget = self.findChild(QDockWidget, "GdbIoView")
            self.pyIoWidget = self.findChild(QDockWidget, "PyIoView")
            self.inferiorIoWidget = self.findChild(QDockWidget, "InferiorIoView")

            #tabify widgets to initial state and save settings
            self.tabifyDockWidget(self.fileListWidget, self.dataGraphWidget)
            self.tabifyDockWidget(self.watchWidget, self.localsWidget)
            self.tabifyDockWidget(self.localsWidget, self.stackWidget)
            self.tabifyDockWidget(self.stackWidget, self.breakpointWidget)
            self.tabifyDockWidget(self.breakpointWidget, self.tracepointWidget)
            self.tabifyDockWidget(self.gdbIoWidget, self.pyIoWidget)
            self.tabifyDockWidget(self.pyIoWidget, self.inferiorIoWidget)

            self.settings.setValue("InitialWindowPlacement/geometry", \
                    self.saveGeometry())
            self.settings.setValue("InitialWindowPlacement/windowState", \
                    self.saveState())

    def initRecentFileHandler(self, nrRecentFiles):
        """
        Create menu entries for recently used files and connect them to the
        RecentFileHandler
        """
        # create menu entries and connect the actions to the debug controller
        recentFileActions = [0] * nrRecentFiles
        for i in range(nrRecentFiles):
            recentFileActions[i] = OpenRecentFileAction(self)
            recentFileActions[i].setVisible(False)
            self.ui.menuRecentlyUsedFiles.addAction(recentFileActions[i])
            recentFileActions[i].executableOpened.connect(self.debugController.openExecutable)

        self.RecentFileHandler = RecentFileHandler(recentFileActions, \
                nrRecentFiles, self.distributedObjects)
        self.debugController.executableOpened.connect(self.RecentFileHandler.addToRecentFiles)

    def restoreInitialWindowPlacement(self):
        """
        Restores the window placement created by
        createInitialWindowPlacement().
        """
        self.restoreGeometry(self.settings.value(\
                "InitialWindowPlacement/geometry").toByteArray())
        self.restoreState(self.settings.value(\
                "InitialWindowPlacement/windowState").toByteArray())

    def showOpenExecutableDialog(self):
        filename = str(QFileDialog.getOpenFileName(self, "Open Executable", self.recentFileHandler.getDirOfLastFile()))
        if (filename != ""):
            self.debugController.openExecutable(filename)

    def showLoadPluginsDialog(self):
        dialog = QFileDialog()
        dialog.setNameFilter("*.xml")
        filename = str(dialog.getOpenFileName(self, "Load plugin configuration"))
        if (filename != ""):
            self.pluginloader.getActivePlugins(filename)

    def showSavePluginsDialog(self):
        dialog = QFileDialog()
        dialog.setNameFilter("*.xml")
        filename = str(dialog.getSaveFileName(self, "Save plugin configuration"))
        if (filename != ""):
            self.pluginloader.savePluginInfo(filename)

    def showExecutableName(self, filename):
        self.ui.actionSaveSession.setEnabled(True)   # enable saving session
        self.setWindowFilePath(filename)

    def targetStartedRunning(self):
        self.ui.statusLabel.setText("Running")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/inferior_running.png"))

    def targetStopped(self, rec):
        self.ui.statusLabel.setText("Stopped")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/inferior_stopped.png"))

    def targetExited(self):
        self.ui.statusLabel.setText("Not running")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/inferior_not_running.png"))

    def closeEvent(self, event):
        if not self.distributedObjects.editorController.closeOpenedFiles():
            event.ignore()  # closing source files may be canceled by user
        else:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            QMainWindow.closeEvent(self, event)
            self.pluginloader.savePluginInfo()

    def readSettings(self):
        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        self.restoreState(self.settings.value("windowState").toByteArray())
