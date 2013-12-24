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

import logging
from helpers.tracer import trace

CLASSNAME = "d"


class ScriptEnv:
    def __init__(self, do):
        self.sp = do.signalProxy
        self.sp.addProxy(["note", "warn", "error", "print_"], self)

    def exec_(self, code):
        try:
            exec(code, {CLASSNAME: self.sp})
        except Exception as e:
            logging.exception(e)

    @trace
    def note(self, *args, **kwargs):
        """show something as a note in the main window"""
        logging.info(*args, **kwargs)

    @trace
    def warn(self, *args, **kwargs):
        """show something as a warning in the main window"""
        logging.warning(*args, **kwargs)

    @trace
    def error(self, *args, **kwargs):
        """show something as an error in the main window"""
        logging.error(*args, **kwargs)

    @trace
    def print_(self, *args):
        """show variables in the main window"""
        for var in args:
            self.note("%s = %s" % (var, self.sp.evaluateExpression(var)))
