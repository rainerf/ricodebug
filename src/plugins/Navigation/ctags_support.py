import ctags
from PyQt4.QtGui import QApplication, QStandardItemModel, QStandardItem, QPixmap, QIcon

class EntryList:
	def __init__(self, filename):
		self.scopes = {}
		self.topLevelEntries = []
		self.model = QStandardItemModel()
		self.model.setHorizontalHeaderLabels(["Name", "File", "Line", "Type"])
		
		e = ctags.TagEntry()
	
		tf = ctags.CTags(filename)
		while tf.next(e):
			self.addFromTagEntry(e)
	
	def getScope(self, scope):
		hier = scope.split("::")
		for s in range(len(hier)):
			scopename = "::".join(hier[0:s+1])
			if scopename not in self.scopes:
				self.scopes[scopename] = Struct(self)
		return self.scopes[scope]

	def addFromTagEntry(self, e):
		kind = e['kind']
		name = e['name']
		file_ = e['file']
		lineNumber = int(e['lineNumber'])
		if e['struct']:
			scope = e['struct']
		elif e['class']:
			scope = e['class']
		else:
			scope = None

		if kind == "class":
			n = self.getScope(scope+"::"+name if scope else name)
			n.setValues(name, file_, lineNumber, scope, Struct.CLASS)
		elif kind == "struct":
			n = self.getScope(scope+"::"+name if scope else name)
			n.setValues(name, file_, lineNumber, scope, Struct.STRUCT)
		elif kind == "function":
			n = Function(self)
			n.setValues(name, file_, lineNumber, scope, e['signature'])
		elif kind == "member" and scope: # namespace members are declared as member, but don't have a scope
			n = Member(self)
			n.setValues(name, file_, lineNumber, scope, {"private": Member.PRIVATE, "protected": Member.PROTECTED, "public": Member.PUBLIC, None: None}[e['access']])
		else:
			n = Entry(self)
			n.setValues(name, file_, lineNumber, scope)

class Entry:
	def __init__(self, entrylist):
		self.scope = None
		self.entrylist = entrylist
		self.items = [QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem()]
		
	def setValues(self, name, file_, lineNumber, scope):
		self.name = name
		self.file_ = file_
		self.lineNumber = lineNumber
		assert not self.scope
		self.scope = scope
		if scope:
			self.entrylist.getScope(scope).children.append(self)
			self.entrylist.getScope(scope).items[0].appendRow(self.items)
		else:
			self.entrylist.topLevelEntries.append(self)
			self.entrylist.model.invisibleRootItem().appendRow(self.items)
		
		self.items[0].setText(name)
		self.items[0].setIcon(QIcon(QPixmap(":/icons/images/var.png")))
		self.items[1].setText(file_)
		self.items[2].setText(str(lineNumber))
		self.items[3].setText("")
		for i in self.items:
			i.setEditable(False)
	
	def __str__(self):
		return "%s %s %s @ %s:%d" % (self.__class__, self.scope, self.name, self.file_, self.lineNumber)

class Struct(Entry):
	STRUCT, CLASS = range(2)
	def __init__(self, entrylist):
		Entry.__init__(self, entrylist)
		self.children = []
	
	def setValues(self, name, file_, lineNumber, scope, kind):
		Entry.setValues(self, name, file_, lineNumber, scope)
		self.kind = kind
		self.items[0].setIcon(QIcon(QPixmap(":/icons/images/struct.png")))
		self.items[3].setText(["struct", "class"][kind])
	
	def __str__(self):
		return "\n".join([Entry.__str__(self)] + ["    " + str(c).replace("\n", "\n    ") for c in self.children])

class Function(Entry):
	def __init__(self, entrylist):
		Entry.__init__(self, entrylist)

	def setValues(self, name, file_, lineNumber, scope, signature):
		Entry.setValues(self, name, file_, lineNumber, scope)
		self.signature = signature
		self.items[0].setText(self.name + self.signature)
		self.items[0].setIcon(QIcon(QPixmap(":/icons/images/sc_process.png")))
		self.items[3].setText("Function")

class Member(Entry):
	PRIVATE, PROTECTED, PUBLIC = range(3)
	def __init__(self, entrylist):
		Entry.__init__(self, entrylist)
		self.items[3].setText("Member")

	def setValues(self, name, file_, lineNumber, scope, access):
		Entry.setValues(self, name, file_, lineNumber, scope)
		self.access = access
		self.items[0].setIcon(QIcon(QPixmap(":/icons/images/var.png")))

def test():
	def viewDoubleClicked(index):
		file_ = index.sibling(index.row(), 1).data().toString()
		line = index.sibling(index.row(), 2).data().toInt()[0]
		print file_, line
	
	import sys
	from PyQt4.QtGui import QTreeView
	from PyQt4.QtCore import QObject, SIGNAL
	app = QApplication(sys.argv)
	widget = QTreeView(None)
	QObject.connect(widget, SIGNAL("doubleClicked(QModelIndex)"), viewDoubleClicked)
	entrylist = EntryList("/home/rainer/tmp/tags")
	widget.setModel(entrylist.model)
	widget.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	test()
