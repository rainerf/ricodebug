from PyQt4.QtCore import QObject, Qt, QSize
from PyQt4.QtGui import QIcon, QBoxLayout
from views.docktoolbar import DockToolBar


class DockToolBarManager(QObject):
    def __init__(self, window):
        QObject.__init__(self, window)
        assert window
        self.main = window
        self.settings = 0
        self.bars = {}

    def bar(self, area):
        if area not in self.bars:
            if area == Qt.TopDockWidgetArea:
                self.bars[area] = DockToolBar(self, Qt.Horizontal, self.main)
                self.bars[area].setObjectName("DockToolBarTop")
                self.bars[area].setWindowTitle("Top toolbar")
                self.bars[area].toggleViewAction().setText("Top toolbar visible")
            elif area == Qt.BottomToolBarArea:
                self.bars[area] = DockToolBar(self, Qt.Horizontal, self.main)
                self.bars[area].setObjectName("DockToolBarBottom")
                self.bars[area].setWindowTitle("Bottom toolbar")
                self.bars[area].toggleViewAction().setText("Bottom toolbar visible")
            elif area == Qt.RightToolBarArea:
                self.bars[area] = DockToolBar(self, Qt.Vertical, self.main)
                self.bars[area].setObjectName("DockToolBarRight")
                self.bars[area].setWindowTitle("Right toolbar")
                self.bars[area].toggleViewAction().setText("Right toolbar visible")
            elif area == Qt.LeftToolBarArea:
                self.bars[area] = DockToolBar(self, Qt.Vertical, self.main)
                self.bars[area].setObjectName("DockToolBarLeft")
                self.bars[area].setWindowTitle("Left toolbar")
                self.bars[area].toggleViewAction().setText("Left toolbar visible")
            else:
                return 0
            self.main.addToolBar(area, self.bars[area])
            self.bars[area].hide()

        self.bars[area].dockWidgetAreaChanged.connect(self.dockWidgetAreaChanged)
        return self.bars[area]

    @staticmethod
    def dockWidgetAreaToToolBarArea(area):
        try:
            return {Qt.LeftDockWidgetArea: Qt.LeftToolBarArea,
                    Qt.RightDockWidgetArea: Qt.RightToolBarArea,
                    Qt.TopDockWidgetArea: Qt.TopToolBarArea,
                    Qt.BottomDockWidgetArea: Qt.BottomToolBarArea}[area]
        except KeyError:
            return Qt.BottomToolBarArea

    @staticmethod
    def toolBarAreaToDockWidgetArea(area):
        return {Qt.LeftToolBarArea: Qt.LeftDockWidgetArea,
                Qt.RightToolBarArea: Qt.RightDockWidgetArea,
                Qt.TopToolBarArea: Qt.TopDockWidgetArea,
                Qt.BottomToolBarArea: Qt.BottomDockWidgetArea}[area]

    @staticmethod
    def toolBarAreaToBoxLayoutDirection(area):
        return {Qt.LeftToolBarArea: QBoxLayout.BottomToTop,
                Qt.RightToolBarArea: QBoxLayout.TopToBottom,
                Qt.TopToolBarArea: QBoxLayout.LeftToRight,
                Qt.BottomToolBarArea: QBoxLayout.LeftToRight}[area]

    def dockWidgetAreaChanged(self, dock, bar):
        bar.removeDock(dock)
        self.bar(self.dockWidgetAreaToToolBarArea(self.main.dockWidgetArea(dock))).addDock(dock, dock.windowTitle(), dock.windowIcon().pixmap(QSize(24, 24), QIcon.Normal, QIcon.On))

    def restoreState(self, bar):
        return

    def saveState(self, bar):
        return
