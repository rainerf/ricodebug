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
from PyQt4.QtGui import QMessageBox
import logging


class Logger(QObject):
    """ Logging class implemented as singleton.
        Writes messages to a file and shows them in pop-ups. """
    _instance = None

    MSG_TYPE_INFO = 0
    MSG_TYPE_WARNING = 1
    MSG_TYPE_ERROR = 2

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = Logger()
        return cls._instance

    def init(self, logFileName, popUpParent):
        """ Initializes logger class. Requires parent for popup and a log filename. """
        #init filename
        if (len(logFileName) != 0):
            self.mainwindow = popUpParent
            self.logFilename = logFileName
            #create file
            self.logger = logging.getLogger(self.logFilename)
            self.logger.setLevel(logging.DEBUG)

            # create file handler and set level to debug
            fhandler = logging.FileHandler(self.logFilename)
            fhandler.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            fhandler.setFormatter(formatter)

            # add handler to logger
            self.logger.addHandler(fhandler)
            self.isInitialized = True

    def __init__(self):
        """ Constructor """
        self.isInitialized = False

    def addLogMessage(self, msgSrc, msgStr, msgType, msgPopUp=False):
        """ Writes a message to the logfile. Opens a popup if msgPopUp is true. """
        if (self.isInitialized == True):
            if (msgType == self.MSG_TYPE_INFO):
                self.logger.info(msgSrc + ": " + msgStr)
                if (msgPopUp == True):
                    QMessageBox.information(None, "Information", msgStr)
            elif (msgType == self.MSG_TYPE_WARNING):
                self.logger.warn(msgSrc + ": " + msgStr)
                if (msgPopUp == True):
                    QMessageBox.warning(None, "Warning", msgStr)
            elif (msgType == self.MSG_TYPE_ERROR):
                self.logger.error(msgSrc + ": " + msgStr)
                if (msgPopUp == True):
                    QMessageBox.critical(self.mainwindow, "Error", msgStr)
