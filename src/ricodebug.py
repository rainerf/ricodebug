#!/usr/bin/env python

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

## @package debugger
# ricodebug's main file.
#
# Execute this file to run ricodebug.

import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import pyqtRemoveInputHook, QDir

sys.path.append(sys.path[0] + '/models')
sys.path.append(sys.path[0] + '/views')
sys.path.append(sys.path[0] + '/controllers')
sys.path.append(sys.path[0] + '/helpers')
sys.path.append(sys.path[0] + '/tests')
sys.path.append(sys.path[0] + '/plugins')
sys.path.append(sys.path[0] + '/variables')
sys.path.append(sys.path[0] + '/datagraph')

from mainwindow import MainWindow
from logger import Logger

## The main routine.
def main():
    pyqtRemoveInputHook()
    QDir(QDir.homePath()).mkdir(".ricodebug")

    app = QApplication(sys.argv)
    app.setApplicationName("ricodebug")
    window = None
    Logger.getInstance().init("logfile", window)
    window = MainWindow()
    if (len(sys.argv) > 1):
        window.openExecutable(sys.argv[1])

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

