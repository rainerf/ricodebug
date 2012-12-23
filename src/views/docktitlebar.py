from PyQt4.QtGui import QToolBar, QWidget, QHBoxLayout, QWidgetAction, QAction, QStylePainter, QStyleOptionToolBar, QDockWidget, QStyle, QTransform, QFontMetrics, QIcon, QFrame, QBoxLayout, QLabel
from PyQt4.QtCore import QSize, QPointF, Qt, QRect, QPoint, QEvent


def qBound(minVal, current, maxVal):
    return max(min(current, maxVal), minVal)


class DockTitleBar(QToolBar):
    def __init__(self, parent):
        QToolBar.__init__(self, parent)
        assert parent
        self.dock = parent

        # a fake spacer widget
        w = QWidget(self)
        l = QHBoxLayout(w)
        l.setMargin(0)
        l.setSpacing(0)
        l.addStretch()

        self.frame = QFrame()
        self.__layout = QBoxLayout(QBoxLayout.LeftToRight, self.frame)
        self.__layout.setContentsMargins(4, 4, 0, 0)
        self.__layout.setSpacing(2)
        self.aDockFrame = self.addWidget(self.frame)

        self.__icon = QLabel()

        self.__layout.addWidget(self.__icon)
        self.__title = QLabel(self.dock.windowTitle())
        self.__layout.addWidget(self.__title)

        self.dock.windowIconChanged.connect(self.__setWindowIcon)

        # fake spacer item
        self.spacer = QWidgetAction(self)
        self.spacer.setDefaultWidget(w)

        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(12, 12))

        self.aFloat = QAction(self)
        self.aClose = QAction(self)

        self.addAction(self.spacer)
        self.addAction(self.aFloat)
        self.addAction(self.aClose)

        self.updateStandardIcons()

        self.dockWidgetFeaturesChanged(self.dock.features())

        self.dock.featuresChanged.connect(self.dockWidgetFeaturesChanged)
        self.aFloat.triggered.connect(self._floatTriggered)
        self.aClose.triggered.connect(self.dock.close)

    def __setWindowIcon(self, icon):
        if not icon.isNull():
            self.__icon.setPixmap(self.dock.windowIcon().pixmap(16))

    def __setWindowTitle(self, title):
        self.__title.setText(title)

    def paintEvent(self, _):
        painter = QStylePainter(self)
        options = QStyleOptionToolBar()

        # init style options
        options.initFrom(self.dock)
        options.rect = self.rect()
        textRect = self.rect().adjusted(3, 3, 0, 0)
        msh = self.minimumSizeHint()

        # need to rotate if vertical state
        if self.dock.features() & QDockWidget.DockWidgetVerticalTitleBar:
            painter.rotate(-90)
            painter.translate(QPointF(-self.rect().height(), 0))
            self.transposeSize(options.rect)
            self.transposeSize(textRect)
            msh.transpose()

        # draw toolbar
        painter.drawControl(QStyle.CE_ToolBar, options)

        # restore rotation
        if self.dock.features() & QDockWidget.DockWidgetVerticalTitleBar:
            painter.rotate(90)

    def transposeSize(self, rect):
        size = rect.size()
        size.transpose()
        rect.setSize(size)

    def updateStandardIcons(self):
        size = QSize(16, 16)
        rect = QRect(QPoint(), self.iconSize())

        transform = QTransform()
        transform.rotate(90)

        pixmap = self.style().standardIcon(QStyle.SP_TitleBarNormalButton, None, self.widgetForAction(self.aFloat)).pixmap(size)
        rect.moveCenter(pixmap.rect().center())
        pixmap = pixmap.copy(rect)
        self.aFloat.setIcon(QIcon(pixmap))

        pixmap = self.style().standardIcon(QStyle.SP_TitleBarCloseButton, None, self.widgetForAction(self.aClose)).pixmap(size)
        rect.moveCenter(pixmap.rect().center())
        pixmap = pixmap.copy(rect)
        self.aClose.setIcon(QIcon(pixmap))

    def event(self, event):
        if event.type() == QEvent.StyleChange:
            self.updateStandardIcons()
        return QToolBar.event(self, event)

    def minimumSizeHint(self):
        return QToolBar.sizeHint(self)

    def sizeHint(self):
        size = QToolBar.sizeHint(self)
        fm = QFontMetrics(self.font())

        if self.dock.features() & QDockWidget.DockWidgetVerticalTitleBar:
            size.setHeight(size.height() + fm.width(self.dock.windowTitle()))
        else:
            size.setWidth(size.width() + fm.width(self.dock.windowTitle()))

        return size

    def _floatTriggered(self):
        self.dock.setFloating(not self.dock.isFloating())

    def dockWidgetFeaturesChanged(self, features):
        self.aFloat.setVisible(features & QDockWidget.DockWidgetFloatable)
        self.aClose.setVisible(features & QDockWidget.DockWidgetClosable)

        # update toolbar orientation
        if features & QDockWidget.DockWidgetVerticalTitleBar:
            if self.orientation() & Qt.Vertical:
                return
            self.setOrientation(Qt.Vertical)
        else:
            if self.orientation() & Qt.Horizontal:
                return
            self.setOrientation(Qt.Horizontal)

        # reorder the actions
        items = self.actions()
        items.reverse()
        self.clear()
        self.addActions(items)
