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
import os


class GDBInit(QObject):
    def __init__(self):
        self.fileName = "load_pretty_printer"
        filePath =  repr(__file__) 
        self.path = filePath[1:filePath.find("helpers/gdbinit.py")] + "third_party/"
        
        self.file_content = []
        self.file_content.append("python\n")
        self.file_content.append("import sys\n")
        self.file_content.append("path=\"" + self.path + "pretty_printer\"\n")
        self.file_content.append("sys.path.insert(0, path)\n")
        self.file_content.append("from libstdcxx.v6.printers import register_libstdcxx_printers\n")
        self.file_content.append("register_libstdcxx_printers (None)\n")
        self.file_content.append("end\n")
          
    def writeFile(self):
        if os.path.exists(self.path + self.fileName):
            os.remove(self.path + self.fileName)
    
        init_script = open(self.path + self.fileName,'w')
        
        for i in self.file_content:
            init_script.write(i)

        init_script.close()
        
    def getPath(self):
        return self.path + self.fileName