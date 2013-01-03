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

from PyQt4.QtGui import QMainWindow, QFileDialog, QLabel, QPixmap, \
        QMenu, QLineEdit, QWidgetAction, QHBoxLayout, QWidget, QFrame
from PyQt4.QtCore import QFileSystemWatcher, Qt
from .ui_mainwindow import Ui_MainWindow
from helpers.distributedobjects import DistributedObjects
from helpers.recentfilehandler import RecentFileHandler
from helpers.pluginloader import PluginLoader
from controllers.quickwatch import QuickWatch
from PyQt4 import QtGui
from widgets.alertabledockwidget import AlertableDockWidget
from widgets.docktoolbarmanager import DockToolBarManager
from views.logview import LogView, LogViewHandler, ErrorLabelHandler


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """ init UI """
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dockToolBarManager = DockToolBarManager(self)

        self.dockToolBar(Qt.TopToolBarArea)
        self.__bottomDockBar = self.dockToolBar(Qt.BottomToolBarArea)
        self.dockToolBar(Qt.LeftToolBarArea)
        self.dockToolBar(Qt.RightToolBarArea)

        self.ui.actionSaveSession.setEnabled(False)

        self.distributedObjects = DistributedObjects(self)

        self.act = self.distributedObjects.actions
        self.debugController = self.distributedObjects.debugController
        self.settings = self.distributedObjects.settings
        self.signalproxy = self.distributedObjects.signalProxy
        self.pluginloader = PluginLoader(self.distributedObjects)
        self.editorController = self.distributedObjects.editorController

        self.act = self.distributedObjects.actions
        # init RecentFileHandler
        self.recentFileHandler = RecentFileHandler(self, self.ui.menuRecentlyUsedFiles, self.distributedObjects)
        self.debugController.executableOpened.connect(self.recentFileHandler.addToRecentFiles)
        self.debugController.executableOpened.connect(self.__observeWorkingBinary)
        self.debugController.executableOpened.connect(self.showExecutableName)
        self.debugController.executableOpened.connect(self.disableButtons)
        # signal proxy
        self.signalproxy.inferiorIsRunning.connect(self.targetStartedRunning)
        self.signalproxy.inferiorStoppedNormally.connect(self.targetStopped)
        self.signalproxy.inferiorReceivedSignal.connect(self.targetStopped)
        self.signalproxy.inferiorHasExited.connect(self.targetExited)

        # Plugin Loader
        self.pluginloader.insertPluginAction.connect(self.addPluginAction)
        self.ui.actionSavePlugins.triggered.connect(self.showSavePluginsDialog)
        self.ui.actionLoadPlugins.triggered.connect(self.showLoadPluginsDialog)

        # Add editor to main window.
        self.ui.gridLayout.addWidget(self.distributedObjects.editorController.editor_view, 0, 0, 1, 1)
        self.logviewhandler = LogViewHandler(LogView())
        self.insertDockWidget(self.logviewhandler.widget, "Log View", Qt.BottomDockWidgetArea, True)
        self.errormsghandler = ErrorLabelHandler(self)

        self.pluginloader.addAvailablePlugins()

        self.setWindowFilePath("<none>")
        self.setupUi()
        self.readSettings()

        self.quickwatch = QuickWatch(self, self.distributedObjects)

        self.binaryName = None
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.fileChanged.connect(self.__binaryChanged)

        self.__runWithArgumentsMenu = None
        self.__argumentsEdit = None
        self.__makeRunWithArgumentsMenu()

    def __makeRunWithArgumentsMenu(self):
        self.__runWithArgumentsMenu = QMenu(self)
        self.__argumentsEdit = QLineEdit()
        self.__argumentsEdit.returnPressed.connect(self.__runWithArgumentsTriggered)

        hl = QHBoxLayout(self.__runWithArgumentsMenu)
        hl.addWidget(QLabel("Run with arguments:"))
        hl.addWidget(self.__argumentsEdit)

        w = QWidget(self.__runWithArgumentsMenu)
        w.setLayout(hl)

        wa = QWidgetAction(self.__runWithArgumentsMenu)
        wa.setDefaultWidget(w)
        self.__runWithArgumentsMenu.addAction(wa)

        self.act.Run.setMenu(self.__runWithArgumentsMenu)

    def __runTriggered(self):
        self.debugController.run()

    def __runWithArgumentsTriggered(self):
        self.__runWithArgumentsMenu.close()
        self.debugController.run(str(self.__argumentsEdit.text()))

    def setupUi(self):
        self.__initActions()
        self.ui.statusLabel = QLabel()
        self.ui.statusLabel.setText("Not running")
        self.ui.statusbar.addPermanentWidget(self.ui.statusLabel)
        self.ui.statusIcon = QLabel()
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/not_running.png"))
        self.ui.statusbar.addPermanentWidget(self.ui.statusIcon)

    def __initActions(self):
        self.disableButtons()
        self.act.Record.setCheckable(True)
        self.act.ReverseNext.setEnabled(False)
        self.act.ReverseStep.setEnabled(False)
        self.act.SaveFile.setEnabled(False)
        # debug actions
        self.ui.menuDebug.addAction(self.act.Run)
        self.ui.menuDebug.addAction(self.act.Continue)
        self.ui.menuDebug.addAction(self.act.Interrupt)
        self.ui.menuDebug.addAction(self.act.Next)
        self.ui.menuDebug.addAction(self.act.Step)
        self.ui.menuDebug.addAction(self.act.Finish)
        self.ui.menuDebug.addAction(self.act.RunToCursor)
        self.ui.menuDebug.addAction(self.act.Record)
        self.ui.menuDebug.addAction(self.act.ReverseNext)
        self.ui.menuDebug.addAction(self.act.ReverseStep)

        # file actions
        self.ui.menuFile.insertAction(self.ui.actionSaveSession,
                self.act.OpenMenu)
        self.ui.menuFile.addAction(self.act.SaveFile)
        self.ui.menuFile.addAction(self.act.Exit)

        # add them to menubar and also menuView to respect order
        self.ui.menubar.addAction(self.ui.menuFile.menuAction())
        self.ui.menubar.addAction(self.ui.menuView.menuAction())
        self.ui.menubar.addAction(self.ui.menuDebug.menuAction())
        self.ui.menubar.addAction(self.ui.menuHelp.menuAction())
        # now make toolbar actions
        self.act.Open.setMenu(self.ui.menuRecentlyUsedFiles)
        self.ui.Main.addAction(self.act.Open)
        self.ui.Main.addAction(self.act.SaveFile)
        self.ui.Main.addSeparator()
        self.ui.Main.addAction(self.act.Run)
        self.ui.Main.addAction(self.act.Continue)
        self.ui.Main.addAction(self.act.Interrupt)
        self.ui.Main.addAction(self.act.Next)
        self.ui.Main.addAction(self.act.Step)
        self.ui.Main.addAction(self.act.Record)
        self.ui.Main.addAction(self.act.ReverseNext)
        self.ui.Main.addAction(self.act.ReverseStep)
        self.ui.Main.addAction(self.act.Finish)
        self.ui.Main.addAction(self.act.RunToCursor)

        self.ui.Main.addSeparator()
        self.ui.Main.addAction(self.act.Exit)
        # connect actions
        self.__connectActions()

    def __connectActions(self):
        # file menu
        self.act.Open.triggered.connect(self.showOpenExecutableDialog)
        self.act.OpenMenu.triggered.connect(self.showOpenExecutableDialog)
        self.act.Exit.triggered.connect(self.close)
        self.act.SaveFile.triggered.connect(self.signalproxy.emitSaveCurrentFile)
        # debug menu

        self.act.Run.triggered.connect(self.__runTriggered)

        self.act.Next.triggered.connect(self.debugController.next_)
        self.act.Step.triggered.connect(self.debugController.step)
        self.act.Continue.triggered.connect(self.debugController.cont)
        self.act.Record.triggered.connect(self.toggleRecord)
        self.act.ReverseStep.triggered.connect(self.debugController.reverse_step)
        self.act.ReverseNext.triggered.connect(self.debugController.reverse_next)

        self.act.Interrupt.triggered.connect(self.debugController.interrupt)
        self.act.Finish.triggered.connect(self.debugController.finish)
        self.act.RunToCursor.triggered.connect(self.debugController.inferiorUntil)

        self.ui.actionRestoreSession.triggered.connect(
                self.distributedObjects.sessionManager.showRestoreSessionDialog)
        self.ui.actionSaveSession.triggered.connect(
                self.distributedObjects.sessionManager.showSaveSessionDialog)
        self.ui.actionConfigure.triggered.connect(self.distributedObjects.configStore.edit)

    def insertDockWidget(self, widget, name, area, addToggleViewAction, icon=None):
        d = AlertableDockWidget(name, self)
        d.setObjectName(name)
        d.setWidget(widget)
        if icon:
            d.setWindowIcon(icon)

        self.dockToolBar(self.dockToolBarManager.dockWidgetAreaToToolBarArea(area)).addDock(d)
        if addToggleViewAction:
            self.ui.menuShow_View.addAction(d.toggleViewAction())

        return d

    def newDockWidget(self, name, area, addToggleViewAction):
        d = AlertableDockWidget(name, self)
        d.setObjectName(name)
        self.dockToolBar(self.dockToolBarManager.dockWidgetAreaToToolBarArea(area)).addDock(d)
        if addToggleViewAction:
            self.ui.menuShow_View.addAction(d.toggleViewAction())

        return d

    def insertStatusbarWidget(self, widget):
        w = QFrame()
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(widget)
        f = QFrame()
        f.setFrameStyle(QFrame.Plain | QFrame.VLine)
        w.layout().addWidget(f)

        self.ui.statusbar.insertPermanentWidget(0, w)
        return w

    def removeStatusbarWidget(self, widget):
        self.ui.statusbar.removeWidget(widget)

    def addPluginAction(self, Action):
        """ show plugin as menu entry """
        self.ui.menuPlugins.addAction(Action)

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
        self.ui.actionSaveSession.setEnabled(True)  # enable saving session
        self.setWindowFilePath(filename)

    def targetStartedRunning(self):
        self.ui.statusLabel.setText("Running")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/running.png"))
        self.disableButtons()
        self.act.Interrupt.setEnabled(True)

    def targetStopped(self, rec):
        self.ui.statusLabel.setText("Stopped")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/stopped.png"))
        self.enableButtons()
        self.act.Interrupt.setEnabled(False)

    def targetExited(self):
        self.ui.statusLabel.setText("Not running")
        self.disableButtons()
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/not_running.png"))

    def closeEvent(self, event):
        if not self.distributedObjects.editorController.closeOpenedFiles():
            event.ignore()  # closing source files may be canceled by user
        else:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.dockToolBarManager.saveState(self.settings)
            QMainWindow.closeEvent(self, event)
            self.pluginloader.savePluginInfo()

    def readSettings(self):
        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        self.restoreState(self.settings.value("windowState").toByteArray())
        self.dockToolBarManager.restoreState(self.settings)

    def toggleRecord(self, check):
        if check:
            self.debugController.record_start()
            self.act.ReverseNext.setEnabled(True)
            self.act.ReverseStep.setEnabled(True)
        else:
            self.debugController.record_stop()
            self.act.ReverseNext.setEnabled(False)
            self.act.ReverseStep.setEnabled(False)

    def enableButtons(self):
        self.act.Continue.setEnabled(True)
        self.act.Interrupt.setEnabled(True)
        self.act.Next.setEnabled(True)
        self.act.Step.setEnabled(True)
        self.act.Finish.setEnabled(True)
        self.act.RunToCursor.setEnabled(True)
        self.act.Record.setEnabled(True)

    def disableButtons(self):
        self.act.Continue.setEnabled(False)
        self.act.Interrupt.setEnabled(False)
        self.act.Next.setEnabled(False)
        self.act.Step.setEnabled(False)
        self.act.Finish.setEnabled(False)
        self.act.RunToCursor.setEnabled(False)
        self.act.Record.setChecked(False)
        self.act.Record.setEnabled(False)

    def __observeWorkingBinary(self, filename):
        """ Private Method to Observe Debugged Binary """
        if self.binaryName != None:
            self.fileWatcher.removePath(self.binaryName)
        self.fileWatcher.addPath(filename)
        self.binaryName = filename

    def __binaryChanged(self):
        """ Slot for FileWatcher - Using QtMessagebox for interaction"""
        box = QtGui.QMessageBox()
        if box.question(self, "Binary Changed!", "Reload File?",
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.debugController.openExecutable(self.binaryName)
        else:
            self.fileWatcher.removePath(self.binaryName)
            self.fileWatcher.addPath(self.binaryName)

    def dockToolBar(self, area):
        return self.dockToolBarManager.bar(area)

