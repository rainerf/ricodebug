# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
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

import ctags
from PyQt4.QtCore import Qt
from operator import attrgetter
from helpers.treemodelhelper import TreeNode, TreeModel
import os.path
from helpers.tools import sort_and_group
from helpers.icons import Icons


class Entry:
    STRUCT, CLASS, FUNCTION, FUNCTION_PRIV, FUNCTION_PROT, MEMBER_PUB, MEMBER_PRIV, MEMBER_PROT, FILE, NAMESPACE, OTHER = range(11)

    def __init__(self, name, file_, line=None, scope=None, type_=None, extra=None):
        self.name = name
        self.file = file_
        self.line = line
        self.scope = scope
        self.type_ = type_
        self.extra = extra
        self.childs = []


class EntryNode(Entry, TreeNode):
    def __init__(self, model, name, file_, line=None, scope=None, type_=None, extra=None):
        Entry.__init__(self, name, file_, line, scope, type_, extra)
        TreeNode.__init__(self, None, model)

    def _getChildren(self):
        return self.childs

    def data(self, c, role):
        def name():
            if self.type_ == self.FILE:
                return "%s (%s)" % (self.name, self.file)
            elif self.type_ == self.FUNCTION:
                return "%s%s" % (self.name, self.extra)
            else:
                return self.name

        if role == Qt.DisplayRole:
            return name()
        elif role == Qt.ToolTipRole:
            info = {
                    self.MEMBER_PRIV: "Private Member",
                    self.MEMBER_PUB: "Public Member",
                    self.MEMBER_PROT: "Protected Member",
                    self.CLASS: "Class",
                    self.STRUCT: "Struct",
                    self.FUNCTION: "Function",
                    self.FUNCTION_PRIV: "Private Function",
                    self.FUNCTION_PROT: "Protected Function",
                    self.FILE: "File",
                    self.NAMESPACE: "Namespace",
                    self.OTHER: "Other"

                }[self.type_]
            if self.line is not None:
                loc = "%s:%s" % (self.file, self.line)
            else:
                loc = self.file
            return "\n".join([name(), info, loc])
        elif role == Qt.DecorationRole:
            try:
                return {
                        self.MEMBER_PRIV: Icons.private_var,
                        self.MEMBER_PUB: Icons.var,
                        self.MEMBER_PROT: Icons.protected_var,
                        self.CLASS: Icons.struct,
                        self.STRUCT: Icons.struct,
                        self.FUNCTION: Icons.function,
                        self.FUNCTION_PRIV: Icons.private_function,
                        self.FUNCTION_PROT: Icons.protected_function,
                        self.FILE: Icons.file,
                        self.NAMESPACE: Icons.namespace,
                        self.OTHER: None
                    }[self.type_]
            except KeyError:
                return None


class EntryModel(TreeModel):
    InternalDataRole = Qt.UserRole

    def __init__(self):
        TreeModel.__init__(self)
        self.__entries = []

    def readFromFile(self, filename, groupByFile, ignorePaths):
        self.__entries = []

        e = ctags.TagEntry()
        tf = ctags.CTags(filename)
        while tf.next(e):
            self.__addFromTagEntry(e, ignorePaths)

        if groupByFile:
            self.__entries = self.__sortByFile(self.__entries)
        else:
            self.__entries = self.__sortByScope(self.__entries, None)
        self.reset()

    def clear(self):
        self.__entries = []
        self.reset()

    def __addFromTagEntry(self, e, ignorePaths):
        kind = e['kind']
        name = e['name']
        file_ = e['file']
        lineNumber = int(e['lineNumber'])
        if e['struct']:
            scope = e['struct']
        elif e['class']:
            scope = e['class']
        elif e['namespace']:
            scope = e['namespace']
        else:
            scope = None

        # allow the user to ignore some paths (system includes, etc.)
        for ip in ignorePaths:
            if ip and file_.startswith(ip):
                return

        add = True
        if kind == "class":
            n = EntryNode(self, name, file_, lineNumber, scope, Entry.CLASS)
        elif kind == "struct":
            n = EntryNode(self, name, file_, lineNumber, scope, Entry.STRUCT)
        elif kind == "function":
            n = EntryNode(self, name, file_, lineNumber, scope, {"private": Entry.FUNCTION_PRIV, "protected": Entry.FUNCTION_PROT, "public": Entry.FUNCTION, None: Entry.FUNCTION}[e['access']], e['signature'])
        elif kind == "member" and scope:  # namespace members are declared as member, but don't have a scope
            n = EntryNode(self, name, file_, lineNumber, scope, {"private": Entry.MEMBER_PRIV, "protected": Entry.MEMBER_PROT, "public": Entry.MEMBER_PUB, None: None}[e['access']])
        elif kind == "namespace":
            n = EntryNode(self, name, file_, lineNumber, scope, Entry.NAMESPACE)
        else:
            n = EntryNode(self, name, file_, lineNumber, scope, Entry.OTHER)

        if add:
            self.__entries.append(n)

    def __sortByFile(self, entries):
        res = []
        for file_, elements in sort_and_group(entries, attrgetter("file")):
            entry = EntryNode(self, os.path.basename(file_), file_, type_=EntryNode.FILE)
            entry.childs = self.__sortByScope(elements, entry)
            for c in entry.childs:
                c.parent = entry

            res.append(entry)

        return res

    def __sortByScope(self, entries, parent):
        def __findParentForScope(scope, parent):
            elem = None

            toSearch = entries
            for part in scope.split("::"):
                for e in toSearch:
                    if e.name == part:
                        elem = e
                        toSearch = e.childs
                        parent = e
                        break
                else:
                    elem = EntryNode(self, part, part)
                    toSearch.append(elem)
                    elem.parent = parent
                    toSearch = elem.childs
                    parent = elem
            return elem

        groups = sort_and_group(entries, attrgetter("scope"))

        # the first group is "None", ie. the top one
        _, x = groups.next()
        entries = list(x)

        for name, elements in groups:
            p = __findParentForScope(name, parent)
            p.childs = list(elements)
            for c in p.childs:
                c.parent = p
        return entries

    def _getRootNodes(self):
        return self.__entries

    def columnCount(self, _):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        t = index.internalPointer()
        if role == self.InternalDataRole:
            return t
        else:
            return t.data(index.column(), role)
