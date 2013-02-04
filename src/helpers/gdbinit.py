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
         
    @staticmethod
    def writeFile(path,fileName):
        init = path + fileName
        
        file_content = []
        file_content.append("python\n")
        file_content.append("import sys\n")
        file_content.append("path=\"" + path + "pretty_printer\"\n")
        file_content.append("sys.path.insert(0, path)\n")
        file_content.append("from libstdcxx.v6.printers import register_libstdcxx_printers\n")
        file_content.append("register_libstdcxx_printers (None)\n")
        file_content.append("end\n")
       
        if os.path.exists(init):
            os.remove(init)
    
        init_script = open(init,'w')
        
        for i in file_content:
            init_script.write(i)

        init_script.close()
        
    def getPath(self):
        return self.path

    def getFileName(self):
        return self.fileName