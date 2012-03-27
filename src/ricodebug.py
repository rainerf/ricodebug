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

import logging
import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import pyqtRemoveInputHook, QDir

from views.mainwindow import MainWindow
from views import logview


def main():
    pyqtRemoveInputHook()
    QDir(QDir.homePath()).mkdir(".ricodebug")

    app = QApplication(sys.argv)
    app.setApplicationName("ricodebug")

    window = MainWindow()

    logviewhandler = logview.LogViewHandler(window.ui.logView, window.ui.filterSlider)
    filehandler = logging.FileHandler(filename='%s/.ricodebug/ricodebug.log' % str(QDir.homePath()))
    window.ui.filterSlider.setValue(3)
    errormsghandler = logview.ErrorLabelHandler(window)
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter('[%(levelname)-8s] : %(filename)15s:%(lineno)4d/%(funcName)-20s : %(message)s')
    filehandler.setFormatter(formatter)
    logger.removeHandler(logger.handlers[0])    # remove the default stream logger
    logger.addHandler(filehandler)
    logger.addHandler(logviewhandler)
    logger.addHandler(errormsghandler)

    if (len(sys.argv) > 1):
        window.debugController.openExecutable(sys.argv[1])

    window.show()
    sys.exit(app.exec_())
    logging.shutdown()

if __name__ == "__main__":
    main()
