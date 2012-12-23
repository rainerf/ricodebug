from PyQt4.QtGui import QToolButton, QBoxLayout, QPixmap, QColor, QStyleOptionToolButton, QPainter, QStyle
from PyQt4.QtCore import QPoint


class RotatableToolButton(QToolButton):
    def __init__(self, parent, direction):
        QToolButton.__init__(self, parent)
        self.setDirection(direction)

    def paintEvent(self, _):
        s = QToolButton.sizeHint(self)
        r = 0
        p = QPoint()

        if self.direction == QBoxLayout.TopToBottom:
            r = 90
            p = QPoint(0, -s.height())
        elif self.direction == QBoxLayout.BottomToTop:
            r = -90
            p = QPoint(-s.width(), 0)

        pixmap = QPixmap(s)
        pixmap.fill(QColor(0, 0, 0, 0))

        o = QStyleOptionToolButton()
        self.initStyleOption(o)

        o.rect.setSize(s)

        pixpainter = QPainter()
        pixpainter.begin(pixmap)
        self.style().drawComplexControl(QStyle.CC_ToolButton, o, pixpainter, self)
        pixpainter.end()

        painter = QPainter(self)
        painter.rotate(r)
        painter.drawPixmap(p, pixmap)

    def sizeHint(self):
        s = QToolButton.sizeHint(self)

        if self.direction in [QBoxLayout.TopToBottom, QBoxLayout.BottomToTop]:
            s.transpose()

        return s

    def setDirection(self, direction):
        self.direction = direction
        self.update()
