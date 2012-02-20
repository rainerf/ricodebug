import ctags
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon
from PyQt4.QtCore import Qt


class EntryList:
    def __init__(self, filename=None):
        self.scopes = {}
        self.topLevelEntries = []
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "File", "Line", "Type"])

        if filename:
            self.readFromFile(filename)

    def readFromFile(self, filename):
        self.scopes = {}
        self.topLevelEntries = []
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Name", "File", "Line", "Type"])

        e = ctags.TagEntry()
        tf = ctags.CTags(filename)
        while tf.next(e):
            self.addFromTagEntry(e)

    def getScope(self, scope):
        hier = scope.split("::")
        for s in range(len(hier)):
            scopename = "::".join(hier[0:s + 1])
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

        # Only add a class/struct if it wasn't present in the file before; this
        # can happen if there are template specializations such as myclass and
        # myclass<T>, which are both represented as myclass in the file. If the
        # entry is present, it will have a line number, so use that as a
        # heuristic ;).
        add = True
        if kind == "class":
            n = self.getScope(scope + "::" + name if scope else name)
            if n.lineNumber == None:
                n.setValues(name, file_, lineNumber, scope, Struct.CLASS)
            else:
                add = False
        elif kind == "struct":
            n = self.getScope(scope + "::" + name if scope else name)
            if n.lineNumber == None:
                n.setValues(name, file_, lineNumber, scope, Struct.STRUCT)
            else:
                add = False
        elif kind == "function":
            n = Function(self)
            n.setValues(name, file_, lineNumber, scope, e['signature'])
        elif kind == "member" and scope:    # namespace members are declared as member, but don't have a scope
            n = Member(self)
            n.setValues(name, file_, lineNumber, scope, {"private": Member.PRIVATE, "protected": Member.PROTECTED, "public": Member.PUBLIC, None: None}[e['access']])
        else:
            n = Entry(self)
            n.setValues(name, file_, lineNumber, scope)
        if add:
            n.addToParent()


class EntryItem(QStandardItem):
    ENTRYROLE = Qt.UserRole + 1

    def __init__(self, entry):
        QStandardItem.__init__(self)
        self.entry = entry

    def data(self, role):
        ret = QStandardItem.data(self, role)
        if role == self.ENTRYROLE:
            return self.entry
        else:
            return ret


class Entry:
    def __init__(self, entrylist):
        self.entrylist = entrylist
        self.scope = None
        self.name = None
        self.file_ = None
        self.lineNumber = None
        self.items = [EntryItem(self), EntryItem(self), EntryItem(self), EntryItem(self)]

    def setValues(self, name, file_, lineNumber, scope):
        self.name = name
        self.file_ = file_
        self.lineNumber = lineNumber
        assert not self.scope
        self.scope = scope

        self.items[0].setText(name)
        self.items[0].setIcon(QIcon(QPixmap(":/icons/images/var.png")))
        self.items[1].setText(file_)
        self.items[2].setText(str(lineNumber))
        self.items[3].setText("")
        for i in self.items:
            i.setEditable(False)

    def addToParent(self):
        if self.scope:
            self.entrylist.getScope(self.scope).children.append(self)
            self.entrylist.getScope(self.scope).items[0].appendRow(self.items)
        else:
            self.entrylist.topLevelEntries.append(self)
            self.entrylist.model.invisibleRootItem().appendRow(self.items)

    def __str__(self):
        return "%s %s %s @ %s:%d" % (self.__class__, self.scope, self.name, self.file_, self.lineNumber)


class Struct(Entry):
    STRUCT, CLASS = range(2)

    def __init__(self, entrylist):
        Entry.__init__(self, entrylist)
        self.children = []
        self.kind = None

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
        self.signature = None

    def setValues(self, name, file_, lineNumber, scope, signature):
        Entry.setValues(self, name, file_, lineNumber, scope)
        self.signature = signature if signature else '()'
        self.items[0].setText(self.name + self.signature)
        self.items[0].setIcon(QIcon(QPixmap(":/icons/images/sc_process.png")))
        self.items[3].setText("Function")


class Member(Entry):
    PRIVATE, PROTECTED, PUBLIC = range(3)

    def __init__(self, entrylist):
        Entry.__init__(self, entrylist)
        self.items[3].setText("Member")
        self.access = None

    def setValues(self, name, file_, lineNumber, scope, access):
        Entry.setValues(self, name, file_, lineNumber, scope)
        self.access = access
        self.items[0].setIcon(QIcon(QPixmap(":/icons/images/var.png")))
