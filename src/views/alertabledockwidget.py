from PyQt4.QtGui import QDockWidget, QTabBar, QColor
from views.docktitlebar import DockTitleBar


class AlertableDockWidget(QDockWidget):
    alertedColor = QColor(255, 0, 0)

    def __init__(self, name, parent=None):
        QDockWidget.__init__(self, name, parent)
        self.titleBar = DockTitleBar(self)
        self.setTitleBarWidget(self.titleBar)

        # we do not know the initial state yet but will get an event on
        # visibilityChanged as soon as the windows are first shown
        self.__visible = None
        self.visibilityChanged.connect(self.__updateVisibility)

    def __findInWindow(self):
        # ok, this is a hack... we search for all QTabBars and see if we find one
        # tab that has the correct text... everything else is well hidden from
        # us by Qt
        for tb in self.parent().findChildren(QTabBar):
            for i in xrange(tb.count()):
                if str(tb.tabText(i)) == str(self.windowTitle()):
                    return (tb, i)
        return (None, None)

    def setAlerted(self):
        # we use self.__visible here since self.isVisible() will return True
        # even if the widget is hidden under another dock widget
        if self.__visible:
            return

        tb, i = self.__findInWindow()
        if tb:
            tb.setTabTextColor(i, self.alertedColor)

    def __updateVisibility(self, visible):
        self.__visible = visible
        if self.__visible:
            self.setNormal()

    def setNormal(self):
        tb, i = self.__findInWindow()
        if tb:
            tb.setTabTextColor(i, self.palette().text().color())
