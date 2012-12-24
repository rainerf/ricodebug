from PyQt4.QtGui import QToolBar, QAction, QFrame, QBoxLayout, QDockWidget, QIcon
from PyQt4.QtCore import QSize, QEvent, Qt, pyqtSignal
from .rotatabletoolbutton import RotatableToolButton


class DockToolBar(QToolBar):
    dockWidgetAreaChanged = pyqtSignal(QDockWidget, QToolBar)

    def __init__(self, manager, orientation, window):
        QToolBar.__init__(self, window)
        assert(manager)
        self.manager = manager
        self.uniqueId = 0

        self.__dockToButton = {}
        self.__buttonToDock = {}

        self.toggleViewAction().setEnabled(False)
        self.toggleViewAction().setVisible(False)

        self.textAlwaysVisible = True

        self.setMovable(False)

        self.aToggleExclusive = QAction(self)
        self.aToggleExclusive.setCheckable(True)
        self.aToggleExclusive.setChecked(True)
        self.aToggleExclusive.setIcon(QIcon(":/icons/images/exclusive.png"))
        self.addAction(self.aToggleExclusive)

        self.setIconSize(QSize(16, 16))

        self.frame = QFrame()

        self.__layout = QBoxLayout(QBoxLayout.LeftToRight, self.frame)
        self.__layout.setMargin(0)
        self.__layout.setSpacing(0)

        self.aDockFrame = self.addWidget(self.frame)

        self.setOrientation(orientation)
        self.__layout.setDirection(QBoxLayout.LeftToRight if orientation == Qt.Horizontal else QBoxLayout.TopToBottom)

    docks = property(lambda self: self.__dockToButton.iterkeys())
    count = property(lambda self: len(self.__dockToButton))
    exclusive = property(lambda self: self.aToggleExclusive.isChecked(), lambda self, value: self.aToggleExclusive.setChecked(value))

    def eventFilter(self, dock, event):
        type_ = event.type()

        if isinstance(dock, QDockWidget):
            if type_ == QEvent.Show or type_ == QEvent.Hide:
                if type_ == QEvent.Show and self.exclusive:
                    self.__hideAllDocksBut(dock)

                btn = self.__dockToButton[dock]
                btn.setChecked(type_ == QEvent.Show)
                self.__checkButtonText(btn)
                self.__checkVisibility()
            elif type_ == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    dock.hide()

        return QToolBar.eventFilter(self, dock, event)

    def hasDock(self, dock):
        return dock in self.__dockToButton

    def addDock(self, dock):
        if not dock:
            raise ValueError

        if self.hasDock(dock):
            return

        tb = self.manager.bar(self.manager.dockWidgetAreaToToolBarArea(self.manager.main.dockWidgetArea(dock)))

        if tb and tb.hasDock(dock):
            tb.removeDock(dock)

        # create button
        pb = RotatableToolButton(self, self.manager.toolBarAreaToBoxLayoutDirection(self.manager.main.toolBarArea(self)))
        pb.setCheckable(True)
        pb.setFont(self.font())
        pb.setText(dock.windowTitle())
        pb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        pb.setIconSize(self.iconSize())
        pb.setIcon(dock.windowIcon())
        pb.show()

        self.__layout.addWidget(pb)

        da = self.manager.main.dockWidgetArea(dock)
        ta = self.manager.toolBarAreaToDockWidgetArea(self.manager.main.toolBarArea(self))

        if da != ta:
            self.manager.main.addDockWidget(ta, dock, self.orientation())

        if self.exclusive and self.count:
            self.__hideAllDocksBut(None)

        pb.setChecked(dock.isVisible())

        self.__checkButtonText(pb)

        self.__buttonToDock[pb] = dock
        self.__dockToButton[dock] = pb

        dock.installEventFilter(self)

        dock.toggleViewAction().changed.connect(self.__dockChanged)
        dock.alerted.connect(self.__dockAlerted)
        dock.windowTitleChanged.connect(self.__dockTitleChanged)
        dock.windowIconChanged.connect(self.__dockIconChanged)
        dock.destroyed.connect(self.__dockDestroyed)
        pb.clicked.connect(self.__buttonClicked)

        self.__checkVisibility()

    def removeDock(self, dock):
        if not isinstance(dock, QDockWidget):
            raise ValueError

        if not self.hasDock(dock):
            return

        dock.removeEventFilter(self)

        dock.toggleViewAction().changed.disconnect(self.__dockChanged)
        dock.alerted.disconnect(self.__dockAlerted)
        dock.windowTitleChanged.disconnect(self.__dockTitleChanged)
        dock.windowIconChanged.disconnect(self.__dockIconChanged)
        dock.destroyed.disconnect(self.__dockDestroyed)

        btn = self.__dockToButton[dock]
        btn.deleteLater()

        del self.__dockToButton[dock]
        del self.__buttonToDock[btn]

        self.__checkVisibility()

    def setExclusive(self, exclusive):
        if self.exclusive == exclusive:
            return
        self.aToggleExclusive.setChecked(exclusive)
        if self.exclusive and self.count:
            self.__hideAllDocksBut(None)

    def toggleExclusiveAction(self):
        self.aToggleExclusive.setText("%s exclusive" % self.windowTitle())
        return self.aToggleExclusive

    def __checkVisibility(self):
        # two actions will always be here: the widget with the buttons and the exclusive action
        if len(self.actions()) > 2 or self.count:
            self.show()
        else:
            self.hide()

    def __checkButtonText(self, b):
        return

        if not b:
            return
        # FIXME
        return

    def __dockChanged(self):
        a = self.sender()
        d = a.parent()

        if not d or d.isFloating() or self.manager.dockWidgetAreaToToolBarArea(self.manager.main.dockWidgetArea(d)) == self.manager.main.toolBarArea(self):
            return
        else:
            self.dockWidgetAreaChanged.emit(d, self)

    def __dockDestroyed(self, o):
        i = self.id(o)
        if i == -1:
            return

        o.removeEventFilter(self)
        b = self.button(o)
        del self.buttons[i]
        b.deleteLater()

        del self.docks[i]

        self.__checkVisibility()

    def __buttonClicked(self, b):
        btn = self.sender()
        dock = self.__buttonToDock[btn]

        if not dock:
            return

        if self.exclusive:
            self.__hideAllDocksBut(dock)

        self.__checkButtonText(btn)

        if dock.isVisible() != b:
            dock.setVisible(b)

    def __hideAllDocksBut(self, toShow=None):
        for dw in self.docks:
            if dw != toShow:
                dw.hide()

    def __dockAlerted(self, alerted):
        dock = self.sender()
        if self.hasDock(dock):
            pb = self.__dockToButton[dock]
            if alerted:
                pb.setStyleSheet("color: red")
            else:
                pb.setStyleSheet("")

    def __dockTitleChanged(self, title):
        dock = self.sender()
        if self.hasDock(dock):
            pb = self.__dockToButton[dock]
            pb.setText(title)

    def __dockIconChanged(self, icon):
        dock = self.sender()
        if self.hasDock(dock):
            pb = self.__dockToButton[dock]
            pb.setIcon(icon)
