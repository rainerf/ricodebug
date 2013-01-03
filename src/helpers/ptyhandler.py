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

"""Linux pseudo terminal handler

Not portable!
"""


import pty
import os
import select
from PyQt4.QtCore import QThread, pyqtSignal


class PtyHandler(QThread):
    dataAvailable = pyqtSignal('QString')

    def __init__(self, parent=None):
        """Initialise Linux pseudo terminal
        """
        QThread.__init__(self, parent)
        self.master, self.slave = pty.openpty()
        self.ptyname = os.ttyname(self.slave)
        self.stop = False

    def run(self):
        """Predifined method by QThread after that is called after start()
        """
        self.listener()

    def listener(self):
        """Listens to the pseudo terminal for new output
        """
        while not self.stop:
            if select.select([self.master], [], [], 0.2) != ([], [], []):
                ret = os.read(self.master, 100)
                self.dataAvailable.emit(ret)

    def write(self, s):
        """Writes to the pseudo terminal
        """
        self.master.write(s)
