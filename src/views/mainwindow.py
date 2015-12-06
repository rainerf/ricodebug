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
from PyQt4.QtCore import Qt

from .ui_mainwindow import Ui_MainWindow
from helpers.distributedobjects import DistributedObjects
from helpers.recentfilehandler import RecentFileHandler
from helpers.pluginloader import PluginLoader
from controllers.quickwatch import QuickWatch
from widgets.alertabledockwidget import AlertableDockWidget
from widgets.docktoolbarmanager import DockToolBarManager
from views.notificationframe import NotificationFrameHandler
from views.logview import LogViewHandler
import logging


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

        self.do = DistributedObjects(self)

        self.act = self.do.actions
        self.debugController = self.do.debugController
        self.settings = self.do.settings
        self.signalproxy = self.do.signalProxy
        self.pluginloader = PluginLoader(self.do)

        self.act = self.do.actions
        # init RecentFileHandler
        self.recentFileHandler = RecentFileHandler(self, self.ui.menuRecentlyUsedFiles, self.do)
        self.debugController.executableOpened.connect(self.recentFileHandler.addToRecentFiles)
        self.debugController.executableOpened.connect(self.showExecutableName)
        self.debugController.executableOpened.connect(self.disableButtons)
        # signal proxy
        self.signalproxy.inferiorIsRunning.connect(self.targetStartedRunning)
        self.signalproxy.inferiorStoppedNormally.connect(self.targetStopped)
        self.signalproxy.inferiorReceivedSignal.connect(self.targetStopped)
        self.signalproxy.inferiorHasExited.connect(self.targetExited)
        self.signalproxy.recordStateChanged.connect(self.setReverseDebugButtonsState)

        # Plugin Loader
        self.pluginloader.insertPluginAction.connect(self.addPluginAction)
        self.ui.actionSavePlugins.triggered.connect(self.showSavePluginsDialog)
        self.ui.actionLoadPlugins.triggered.connect(self.showLoadPluginsDialog)

        dw = self.insertDockWidget(None, "Log View", Qt.BottomDockWidgetArea, True)
        self.logviewhandler = LogViewHandler(dw)
        dw.setWidget(self.logviewhandler)
        self.notificationFrameHandler = NotificationFrameHandler(self.ui.notificationArea)

        self.pluginloader.addAvailablePlugins()

        self.setWindowFilePath("<none>")
        self.setupUi()
        self.readSettings()

        self.quickwatch = QuickWatch(self, self.do)

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
        self.act.ReverseFinish.setEnabled(False)
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
        self.__makeRunWithArgumentsMenu()
        self.ui.Main.addAction(self.act.Run)
        self.ui.Main.addAction(self.act.Continue)
        self.ui.Main.addAction(self.act.Interrupt)
        self.ui.Main.addAction(self.act.Next)
        self.ui.Main.addAction(self.act.Step)
        self.ui.reverseBar.addAction(self.act.Record)
        self.ui.reverseBar.addAction(self.act.ReverseNext)
        self.ui.reverseBar.addAction(self.act.ReverseStep)
        self.ui.reverseBar.addAction(self.act.ReverseFinish)
        self.ui.Main.addAction(self.act.Finish)
        self.ui.Main.addAction(self.act.RunToCursor)

        self.ui.Main.addSeparator()
        self.ui.Main.addAction(self.act.Exit)
        # connect actions
        self.__connectActions()

    def __connectActions(self):
        self.ui.actionRestoreSession.triggered.connect(
                self.do.sessionManager.showRestoreSessionDialog)
        self.ui.actionSaveSession.triggered.connect(
                self.do.sessionManager.showSaveSessionDialog)
        self.ui.actionConfigure.triggered.connect(self.do.configStore.edit)

    def insertDockWidget(self, widget, name, area, addToggleViewAction, icon=None):
        d = AlertableDockWidget(name, self)
        d.setObjectName(name)
        if widget:
            d.setWidget(widget)
        if icon:
            d.setWindowIcon(icon)

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
        if filename != "":
            self.debugController.openExecutable(filename)

    def showLoadPluginsDialog(self):
        dialog = QFileDialog()
        dialog.setNameFilter("*.xml")
        filename = str(dialog.getOpenFileName(self, "Load plugin configuration"))
        if filename != "":
            self.pluginloader.getActivePlugins(filename)

    def showSavePluginsDialog(self):
        dialog = QFileDialog()
        dialog.setNameFilter("*.xml")
        filename = str(dialog.getSaveFileName(self, "Save plugin configuration"))
        if filename != "":
            self.pluginloader.savePluginInfo(filename)

    def showExecutableName(self, filename):
        self.ui.actionSaveSession.setEnabled(True)  # enable saving session
        self.setWindowFilePath(filename)

    def targetStartedRunning(self):
        self.ui.statusLabel.setText("Running")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/running.png"))
        self.disableButtons()
        self.act.Interrupt.setEnabled(True)

    def targetStopped(self, _):
        self.ui.statusLabel.setText("Stopped")
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/stopped.png"))
        self.enableButtons()
        self.act.Interrupt.setEnabled(False)

    def targetExited(self):
        self.ui.statusLabel.setText("Not running")
        self.disableButtons()
        self.ui.statusIcon.setPixmap(QPixmap(":/icons/images/22x22/not_running.png"))
        logging.info("Inferior exited.")

    def closeEvent(self, event):
        if not self.do.editorController.closeOpenedFiles():
            event.ignore()  # closing source files may be canceled by user
        else:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.dockToolBarManager.saveState(self.settings)
            QMainWindow.closeEvent(self, event)
            self.pluginloader.savePluginInfo()

    def readSettings(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        windowState = self.settings.value("windowState")
        if windowState:
            self.restoreState(windowState)
        self.dockToolBarManager.restoreState(self.settings)

    def setReverseDebugButtonsState(self, check):
        self.act.ReverseNext.setEnabled(check)
        self.act.ReverseStep.setEnabled(check)
        self.act.ReverseFinish.setEnabled(check)

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

    def dockToolBar(self, area):
        return self.dockToolBarManager.bar(area)
