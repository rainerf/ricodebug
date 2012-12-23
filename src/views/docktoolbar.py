from PyQt4.QtGui import QToolBar, QAction, QFrame, QBoxLayout, QDockWidget, QAbstractButton, QPushButton, QIcon, QLabel
from PyQt4.QtCore import QSize, QEvent, Qt, pyqtSignal
import copy


class DockToolBar(QToolBar):
    dockWidgetAreaChanged = pyqtSignal(QDockWidget, QToolBar)
    buttonClicked = pyqtSignal(int)

    def __init__(self, manager, orientation, window):
        QToolBar.__init__(self, window)
        assert(manager)
        self.manager = manager
        self.uniqueId = 0

        self.docks = {}
        self.buttons = {}

        self.toggleViewAction().setEnabled(False)
        self.toggleViewAction().setVisible(False)

        self.textAlwaysVisible = True

        self.setMovable(False)

        self.aToggleExclusive = QAction(self)
        self.aToggleExclusive.setCheckable(True)
        self.aToggleExclusive.setChecked(True)

        self.setIconSize(QSize(16, 16))

        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: red")

        self.__layout = QBoxLayout(QBoxLayout.LeftToRight, self.frame)
        self.__layout.setMargin(0)
        self.__layout.setSpacing(0)

        self.aDockFrame = self.addWidget(self.frame)

        self.orientationChanged.connect(self.internal_orientationChanged)

        self.setOrientation(orientation)

    def eventFilter(self, object, event):
        type = event.type()
        dock = object

        if isinstance(dock, QDockWidget):
            if type == QEvent.Show or type == QEvent.Hide:
                if type == QEvent.Show and self.aToggleExclusive.isChecked():
                    for dw in self.docks.itervalues():
                        if dw != dock and dw.isVisible():
                            dw.hide()

                btn = self.button(dock)
                btn.setChecked(type == QEvent.Show)
                self.internal_checkButtonText(btn)
                self.internal_checkVisibility()
            elif type == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    dock.hide()

        return QToolBar.eventFilter(self, object, event)

#    def addAction(self, action, insert):
#        if not action:
#            action = QAction(self)
#            action.setSeparator(True)
#
#        if insert:
#            QToolBar.insertAction(self, self.aDockFrame, action)
#        else:
#            QToolBar.addAction(action)
#
#        self.internal_checkVisibility()
#
#        return action

#    def addActions(self, actions, insert):
#        if insert:
#            QToolBar.insertActions(self, self.aDockFrame, actions)
#        else:
#            QToolBar.addActions(actions)
#
#        self.internal_checkVisibility()

    def addDock(self, dock, title, icon):
        if not dock or self.id(dock) != -1:
            return -1

        tb = self.manager.bar(self.manager.dockWidgetAreaToToolBarArea(self.manager.main.dockWidgetArea(dock)))

        if tb and tb.id(dock) != -1:
            tb.removeDock(dock)

        if title:
            dock.setWindowTitle(title)

        if dock.objectName().isEmpty():
            dock.setObjectName(("QDockWidget_%s" % (title)).replace(" ", "_"))

        if not icon.isNull():
            dock.setWindowIcon(icon)

        # create button
        # pb = QPushButton(self, self.manager.toolBarAreaToBoxLayoutDirection(self.manager.main.toolBarArea(self)))
        pb = QPushButton(self.frame)
        pb.setCheckable(True)
        pb.setFont(self.font())
        pb.setText(dock.windowTitle())
        pb.setToolTip(pb.text())
        pb.setProperty("Caption", pb.text())
        # pb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        pb.setIconSize(self.iconSize())
        pb.setIcon(QIcon(icon))
        pb.show()

        self.__layout.addWidget(pb)

        da = self.manager.main.dockWidgetArea(dock)
        ta = self.manager.toolBarAreaToDockWidgetArea(self.manager.main.toolBarArea(self))

        if da != ta:
            self.manager.main.addDockWidget(ta, dock, self.orientation())

        if self.aToggleExclusive.isChecked() and self.count():
            for dw in copy.copy(self.docks.values()):
                if dw.isVisible():
                    dw.hide()

        pb.setChecked(dock.isVisible())

        self.internal_checkButtonText(pb)

        self.buttons[self.uniqueId] = pb
        self.docks[self.uniqueId] = dock

        dock.installEventFilter(self)

        dock.toggleViewAction().changed.connect(self.internal_dockChanged)
        dock.destroyed.connect(self.internal_dockDestroyed)
        pb.clicked.connect(self.internal_buttonClicked)

        self.internal_checkVisibility()

        self.uniqueId += 1
        return self.uniqueId - 1

    def removeDock(self, dock):
        if not isinstance(dock, QDockWidget):
            dock = self.dock(dock)

        i = self.id(dock)

        if i == -1:
            return

        dock.removeEventFilter(self)

        dock.toggleViewAction().changed.disconnect(self.internal_dockChanged)
        dock.destroyed.disconnect(self.internal_dockDestroyed)

        btn = self.button(dock)
        del self.buttons[i]
        btn.deleteLater()

        del self.docks[i]

        self.internal_checkVisibility()

    def isDockVisible(self, dock):
        if not isinstance(dock, QDockWidget):
            dock = self.dock(dock)

        if self.id(dock) != -1:
            return self.button(dock).isChecked()

        return dock.isVisible() if dock else False

    def setDockVisible(self, dock, visible):
        dock.setVisible(visible)

    def exclusive(self):
        return self.aToggleExclusive.isChecked()

    def setExclusive(self, exclusive):
        if self.aToggleExclusive.isChecked() == exclusive:
            return
        self.aToggleExclusive.setChecked(exclusive)
        if self.aToggleExclusive.isChecked() and self.count():
            for dw in self.docks.itervalues():
                if dw.isVisible():
                    dw.hide()

    def id(self, x):
        if isinstance(x, QDockWidget):
            for k, v in self.docks.items():
                if v == x:
                    return k
            return -1
        elif isinstance(x, QAbstractButton):
            for k, v in self.buttons.items():
                if v == x:
                    return k
            return -1
        else:
            raise

    def dock(self, x):
        if isinstance(x, QAbstractButton):
            return self.dock(self.id(x))
        else:
            return self.docks[x]

    def button(self, x):
        if isinstance(x, QDockWidget):
            return self.button(self.id(x))
        else:
            return self.buttons[x]

    def count(self):
        return len(self.docks)

    def toggleExclusiveAction(self):
        self.aToggleExclusive.setText("%s exclusive" % self.windowTitle())
        return self.aToggleExclusive

    def internal_checkVisibility(self):
        i = len(self.actions())

        if not self.isVisible() and (i > 1 or (i == 1 and self.count())):
            self.show()
        elif self.isVisible() and (i == 1 and not self.count()):
            self.hide()

    def internal_checkButtonText(self, b):
        return

        if not b:
            return
        # FIXME
        return

    def internal_orientationChanged(self, o):
        if o == Qt.Horizontal:
            self.__layout.setDirection(QBoxLayout.LeftToRight)
        else:
            self.__layout.setDirection(QBoxLayout.TopToBottom)

        for d in self.docks.itervalues():
            self.manager.main.addDockWdiget(self.manager.main.dockWidgetArea(d), d, o)

    def internal_dockChanged(self):
        a = self.sender()
        d = a.parent()

        if not d or d.isFloating() or self.manager.dockWidgetAreaToToolBarArea(self.manager.main.dockWidgetArea(d)) == self.manager.main.toolBarArea(self):
            return
        else:
            self.dockWidgetAreaChanged.emit(d, self)

    def internal_dockDestroyed(self, o):
        i = self.id(o)
        if i == -1:
            return

        o.removeEventFilter(self)
        b = self.button(o)
        del self.buttons[i]
        b.deleteLater()

        del self.docks[i]

        self.internal_checkVisibility()

    def internal_buttonClicked(self, b):
        ab = self.sender()
        d = self.dock(ab)

        if not d:
            return

        if self.aToggleExclusive.isChecked():
            for dw in self.docks.itervalues():
                if dw != d and dw.isVisible():
                    dw.hide()

        self.internal_checkButtonText(ab)

        if d.isVisible() != b:
            d.setVisible(b)

        self.buttonClicked.emit(self.id(self.dock(ab)))
