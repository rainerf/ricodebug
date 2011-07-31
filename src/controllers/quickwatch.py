from PyQt4.QtGui import QToolBar, QLineEdit, QIcon
from PyQt4.QtCore import QObject

class QuickWatch(QToolBar):
    def __init__(self, parent, distributed_objects):
        QObject.__init__(self, "QuickWatch")
        self.setObjectName("QuickWatch")
        parent.addToolBar(self)
        self.watchedit = QLineEdit()
        self.watchedit.setFixedHeight(28)
        self.addWidget(self.watchedit)
        self.distributed_objects = distributed_objects
        self.addAction(QIcon(":/icons/images/watch.png"), "Add to Watch", self.addToWatch)
        self.addAction(QIcon(":/icons/images/datagraph.png"), "Add to Data Graph", self.addToDG)
    
    def addToWatch(self):
        self.distributed_objects.watch_controller.addWatch(self.watchedit.toPlainText())

    def addToDG(self):
        self.distributed_objects.datagraph_controller.addWatch(self.watchedit.toPlainText())
