from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QBoxLayout, QDockWidget
from .docktoolbar import DockToolBar


class DockToolBarManager(QObject):
    def __init__(self, window):
        QObject.__init__(self, window)
        assert window
        self.main = window
        self.bars = {}

    def bar(self, area):
        if area not in self.bars:
            direction, name = {
                    Qt.LeftDockWidgetArea: (Qt.Vertical, "Left"),
                    Qt.RightDockWidgetArea: (Qt.Vertical, "Right"),
                    Qt.TopDockWidgetArea: (Qt.Horizontal, "Top"),
                    Qt.BottomDockWidgetArea: (Qt.Horizontal, "Bottom")}[area]

            self.bars[area] = DockToolBar(self, direction, self.main)
            self.bars[area].setObjectName("DockToolBar%s" % name)
            self.bars[area].setWindowTitle("%s toolbar" % name)
            self.bars[area].toggleViewAction().setText("%s toolbar visible %name")

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
        self.bar(self.dockWidgetAreaToToolBarArea(self.main.dockWidgetArea(dock))).addDock(dock)

    def restoreState(self, settings):
        settings.beginGroup("Mainwindow/Docks")
        areas = settings.childGroups()

        for area in areas:
            area, ok = area.toInt()
            assert ok

            bar = self.bar(area)
            bar.exclusive = settings.value("%s/Exclusive" % area).toBool()
            names = map(str, list(settings.value("%s/Widgets" % area).toStringList()))
            for name in names:
                dock = self.main.findChild(QDockWidget, name)
                if dock:
                    bar.addDock(dock)

        settings.endGroup()

    def saveState(self, settings):
        for bar in self.bars.values():
            names = [w.objectName() for w in bar.docks]

            settings.setValue("Mainwindow/Docks/%s/Exclusive" % self.main.toolBarArea(bar), bar.exclusive)
            settings.setValue("Mainwindow/Docks/%s/Widgets" % self.main.toolBarArea(bar), names)
