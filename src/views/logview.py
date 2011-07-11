import logging
from PyQt4.QtGui import QTableView, QLabel, QTextEdit, QWidget, QGridLayout, QProgressBar, QMessageBox, QApplication, QStyle, QFrame, QPalette, QBrush
from PyQt4.QtCore import Qt, SIGNAL, pyqtSlot, QTimer, QObject
from logmodel import LogModel, FilteredLogModel

class LogViewHandler(logging.Handler):
    def __init__(self, target_widget, filter_slider):
        logging.Handler.__init__(self)
        self.target_widget = target_widget
        self.model = LogModel()
        self.filter_model = FilteredLogModel()
        self.filter_model.setSourceModel(self.model)
        target_widget.setModel(self.filter_model)
        self.target_widget = target_widget
        QObject.connect(filter_slider, SIGNAL("valueChanged(int)"), self.setFilter)
    
    def emit(self, record):
        self.model.insertMessage(record)
        self.target_widget.resizeColumnsToContents()
        if self.target_widget.columnWidth(2)> 500:
            self.target_widget.setColumnWidth(2, 500)
        self.target_widget.scrollToBottom()

    def setFilter(self, value):
        self.filter_model.setMinimum(value*10)

class ErrorLabel(QWidget):
    WARNING, ERROR = range(2)
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.ticks = 5
        self.elapsedTicks= 0
        self.lastSeverity = None
        self.icon_label = QLabel()
        self.icon_label.setGeometry(0, 0, 48, 48)
        self.message_edit = QTextEdit()
        self.message_edit.setReadOnly(True)
        self.message_edit.setFrameStyle(QFrame.NoFrame)
        palette = self.message_edit.palette()
        palette.setBrush(QPalette.Base, QBrush())
        self.message_edit.setPalette(palette)
        self.time_bar = QProgressBar()
        self.time_bar.setOrientation(Qt.Vertical)
        self.time_bar.setMaximum(self.ticks)
        self.time_bar.setTextVisible(False)
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.time_bar, 0, 0)
        self.layout.addWidget(self.icon_label, 0, 1)
        self.layout.addWidget(self.message_edit, 0, 2)
        self.layout.setColumnStretch(2, 1)
        self.setAutoFillBackground(True)
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.decrementTime)

    def mousePressEvent(self, e):
        self.timer.stop()
        self.hide()
        [QMessageBox.warning, QMessageBox.critical][self.lastSeverity](self.parent(), "Error", self.message_edit.toPlainText())

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
        self.message_edit.setText(msg)
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
        if record.levelno >= logging.ERROR:
            self.error_label.setErrorMessage("<b>%s</b>" % record.message)
        elif record.levelno >= logging.WARNING:
            self.error_label.setWarningMessage("<b>%s</b>" % record.message)



class LogView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
