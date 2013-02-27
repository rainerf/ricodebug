import logging
from PyQt4.QtGui import QApplication, QStyle, QColor, QFrame

from views.ui_notificationframe import Ui_NotificationFrame


class NotificationFrame(QFrame):
    POSITIVE, INFO, WARNING, ERROR = range(4)

    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.ui = Ui_NotificationFrame()

        self._data = {
            self.POSITIVE: ("#6ebe8a", None),
            self.INFO: ("#4398c8", QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation).pixmap(36, 36)),
            self.WARNING: ("#d0b05f", QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(36, 36)),
            self.ERROR: ("#cda8a8", QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(36, 36))
            }

        self.ui.setupUi(self)
        self.hide()

    def setMessage(self, msg, severity):
        self.ui.messageLabel.setText(msg)
        self.setColor(self._data[severity][0])
        self.ui.iconLabel.setPixmap(self._data[severity][1])
        self.show()

    def setColor(self, color):
        stylesheet = \
        """
        #notificationFrame {
          border-radius: 5px;
          padding: 2px;
          background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 0.1 %s, stop: 1 %s);
          border: 1px solid %s;
        }"""

        def lighter(c):
            return QColor(c).lighter(110).name()

        def darker(c):
            return QColor(c).darker(110).name()

        self.setStyleSheet(stylesheet % (lighter(color), color, darker(color), "black"))


class NotificationFrameHandler(logging.Handler):
    def __init__(self, notificationFrame):
        logging.Handler.__init__(self)
        self._notificationFrame = notificationFrame

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self._notificationFrame.setMessage(record.message, self._notificationFrame.ERROR)
        elif record.levelno >= logging.WARNING:
            self._notificationFrame.setMessage(record.message, self._notificationFrame.WARNING)
