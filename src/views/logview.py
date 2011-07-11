import logging
from PyQt4.QtGui import QTableView, QLabel, QWidget, QGridLayout, QProgressBar, QMessageBox, QApplication, QStyle
from PyQt4.QtCore import Qt, SIGNAL, pyqtSlot, QTimer
from logmodel import LogModel

class LogViewHandler(logging.Handler):
    def __init__(self, target_widget):
        logging.Handler.__init__(self)
        self.target_widget = target_widget
        self.model = LogModel()
        target_widget.setModel(self.model)
        self.target_widget = target_widget
    
    def emit(self, record):
        self.model.insertMessage(record)
        self.target_widget.resizeColumnsToContents()
        if self.target_widget.columnWidth(2)> 500:
            self.target_widget.setColumnWidth(2, 500)
        self.target_widget.scrollToBottom()


class ErrorLabel(QWidget):
    WARNING, ERROR = range(2)
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.ticks = 5
        self.elapsedTicks= 0
        self.lastSeverity = None
        self.icon_label = QLabel()
        self.icon_label.setGeometry(0, 0, 48, 48)
        self.message_label = QLabel()
        self.time_bar = QProgressBar()
        self.time_bar.setOrientation(Qt.Vertical)
        self.time_bar.setMaximum(self.ticks)
        self.time_bar.setTextVisible(False)
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.time_bar, 0, 0)
        self.layout.addWidget(self.icon_label, 0, 1)
        self.layout.addWidget(self.message_label, 0, 2)
        self.layout.setColumnStretch(2, 1)
        self.setAutoFillBackground(True)
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.decrementTime)

    def mousePressEvent(self, e):
        self.timer.stop()
        self.hide()
        [QMessageBox.warning, QMessageBox.critical][self.lastSeverity](self.parent(), "Error", self.message_label.text())

    @pyqtSlot()
    def decrementTime(self):
        if self.elapsedTicks == self.ticks:
            self.hide()
            self.timer.stop()
        else:
            self.elapsedTicks += 1
            self.time_bar.setValue(self.ticks - self.elapsedTicks)

    def updatePosition(self):
        self.setGeometry(0, self.parent().height()-self.height(), self.width(), self.height())
    
    def setSize(self, w, h):
        self.setGeometry(0, self.parent().height()-h, w, h)
    
    def setErrorMessage(self, msg):
        self.lastSeverity = self.ERROR
        self.icon_label.setPixmap(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(48, 48))
        self._setMessage(msg)

    def setWarningMessage(self, msg):
        self.lastSeverity = self.WARNING
        self.icon_label.setPixmap(QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(48, 48))
        self._setMessage(msg)
        
    def _setMessage(self, msg):
        self.message_label.setText(msg)
        self.updatePosition()
        self.elapsedTicks= 0
        self.time_bar.setValue(self.ticks)
        self.timer.start(1000)
        self.show()


class ErrorLabelHandler(logging.Handler):
    def __init__(self, main_window):
        logging.Handler.__init__(self)
        self.main_window = main_window
        
        self.error_label = ErrorLabel(main_window)
        self.error_label.setSize(500, 100)
        self.error_label.hide()

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            self.error_label.setWarningMessage("<b>%s</b>" % record.message)
        elif record.levelno >= logging.ERROR:
            self.error_label.setErrorMessage("<b>%s</b>" % record.message)


class LogView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
