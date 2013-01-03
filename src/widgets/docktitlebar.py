# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2012  he ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# Copyright (C) 2005 - 2011  Filipe AZEVEDO & The Monkey Studio Team
# http://monkeystudio.org licensing under the GNU GPL.
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

from PyQt4.QtGui import QToolBar, QWidget, QHBoxLayout, QWidgetAction, \
        QAction, QStylePainter, QStyleOptionToolBar, QDockWidget, QStyle, \
        QTransform, QFontMetrics, QIcon, QFrame, QBoxLayout, QLabel
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

        frame = QFrame()
        layout = QBoxLayout(QBoxLayout.LeftToRight, frame)
        layout.setContentsMargins(4, 4, 0, 0)
        layout.setSpacing(2)
        self.aDockFrame = self.addWidget(frame)

        self.__icon = QLabel()

        layout.addWidget(self.__icon)
        layout.addWidget(QLabel(self.dock.windowTitle()))

        self.dock.windowIconChanged.connect(self.__setWindowIcon)

        # fake spacer item
        spacer = QWidgetAction(self)
        spacer.setDefaultWidget(w)

        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(12, 12))

        self.aFloat = QAction(self)
        self.aClose = QAction(self)

        QToolBar.addAction(self, spacer)
        self.separator = QToolBar.addSeparator(self)
        QToolBar.addAction(self, self.aFloat)
        QToolBar.addAction(self, self.aClose)

        self.updateStandardIcons()

        self.dockWidgetFeaturesChanged(self.dock.features())

        self.dock.featuresChanged.connect(self.dockWidgetFeaturesChanged)
        self.aFloat.triggered.connect(self._floatTriggered)
        self.aClose.triggered.connect(self.dock.close)

    def addAction(self, action):
        self.insertAction(self.separator, action)
        return action

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

    @staticmethod
    def transposeSize(rect):
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
