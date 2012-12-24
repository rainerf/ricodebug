from PyQt4.QtGui import QDockWidget, QIcon, QAction
from PyQt4.QtCore import pyqtSignal
from .docktitlebar import DockTitleBar


class AlertableDockWidget(QDockWidget):
    windowIconChanged = pyqtSignal(QIcon)
    windowTitleChanged = pyqtSignal(str)
    alerted = pyqtSignal(bool)
    clearRequested = pyqtSignal()

    def __init__(self, name, parent, clearAction=False):
        QDockWidget.__init__(self, name, parent)
        self.titleBar = DockTitleBar(self)
        self.setTitleBarWidget(self.titleBar)

        # we do not know the initial state yet but will get an event on
        # visibilityChanged as soon as the windows are first shown
        self.__visible = None
        self.visibilityChanged.connect(self.__updateVisibility)

    def addClearAction(self):
        self.addAction(QAction(QIcon(":/icons/images/clear.png"), "Clear", self)).triggered.connect(lambda: self.clearRequested.emit())

    def addAction(self, action):
        return self.titleBarWidget().addAction(action)

    def setAlerted(self):
        if self.__visible:
            return
        self.alerted.emit(True)

    def __updateVisibility(self, visible):
        self.__visible = visible
        if self.__visible:
            self.setNormal()

    def setNormal(self):
        self.alerted.emit(False)

    def setWindowIcon(self, icon):
        QDockWidget.setWindowIcon(self, icon)
        self.windowIconChanged.emit(icon)

    def setWindowTitle(self, text):
        QDockWidget.setWindowTitle(self, text)
        self.windowTitleChanged.emit(text)
