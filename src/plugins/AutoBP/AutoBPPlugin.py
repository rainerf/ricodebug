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

from PyQt4.QtCore import QObject


class AutoBPPlugin(QObject):
    def __init__(self):
        QObject.__init__(self)

    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""

        self.signalproxy = signalproxy
        self.signalproxy.distributedObjects.debugController.executableOpened.connect(self.update)

        # load the breakpoints if the plugin was loaded after the executable
        self.update()

    def deInitPlugin(self):
        pass

    def update(self):
        sources = self.signalproxy.distributedObjects.gdb_connector.getSources()
        for s in sources:
            with open(s) as f:
                for i, line in enumerate(f):
                    if '// bp' in line:
                        self.signalproxy.distributedObjects.breakpointController.insertBreakpoint(s, i + 1)
