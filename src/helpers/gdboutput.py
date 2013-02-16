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

"""
Predefined constants for the gdb output
"""


class GdbOutput:
    RESULT_RECORD, \
    EXEC_ASYN, \
    STATUS_ASYN, \
    NOTIFY_ASYN, \
    CONSOLE_STREAM, \
    TARGET_STREAM, \
    LOG_STREAM, \
    DONE, \
    RUNNING, \
    STOPPED, \
    THREAD_CREATED, \
    THREAD_GROUP_CREATED, \
    THREAD_GROUP_ADDED, \
    THREAD_GROUP_STARTED, \
    THREAD_EXITED, \
    THREAD_GROUP_EXITED, \
    THREAD_SELECTED, \
    LIBRARY_LOADED, \
    LIBRARY_UNLOADED, \
    BREAKPOINT_MODIFIED, \
    BREAKPOINT_CREATED, \
    EXIT, \
    CONNECTED, \
    ERROR \
 = range(24)

    def __init__(self):
        self.class_ = None  # done, running,...
        self.string = None  # the string of a stream output
        self.type_ = None  # the type of a async response
