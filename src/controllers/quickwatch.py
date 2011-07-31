from PyQt4.QtGui import QToolBar, QTextEdit
from PyQt4.QtCore import QObject

class QuickWatch(QToolBar):
    def __init__(self, parent, distributed_objects):
        QObject.__init__(self, "QuickWatch")
        parent.addToolBar(self)
        self.watchedit = QTextEdit()
        self.watchedit.setFixedHeight(28)
        self.addWidget(self.watchedit)
        self.distributed_objects = distributed_objects
        self.addAction("Add to Watch", self.addToWatch)
        self.addAction("Add to Data Graph", self.addToDG)
    
    def addToWatch(self):
        self.distributed_objects.watch_controller.addWatch(self.watchedit.toPlainText())

    def addToDG(self):
        self.distributed_objects.datagraph_controller.addWatch(self.watchedit.toPlainText())
