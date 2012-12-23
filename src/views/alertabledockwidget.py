from PyQt4.QtGui import QDockWidget, QIcon
from PyQt4.QtCore import pyqtSignal
from views.docktitlebar import DockTitleBar


class AlertableDockWidget(QDockWidget):
    windowIconChanged = pyqtSignal(QIcon)
    windowTitleChanged = pyqtSignal(str)
    alerted = pyqtSignal(bool)

    def __init__(self, name, parent):
        QDockWidget.__init__(self, name, parent)
        self.titleBar = DockTitleBar(self)
        self.setTitleBarWidget(self.titleBar)

        # we do not know the initial state yet but will get an event on
        # visibilityChanged as soon as the windows are first shown
        self.__visible = None
        self.visibilityChanged.connect(self.__updateVisibility)

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
