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


def _getAvailableFiltes():
    return [Empty, Hex, Bin]


def add_actions_for_all_filters(menu, varWrapper):
    def setFilter(varWrapper, filter_):
        def f():
            varWrapper.setFilter(filter_)
        return f

    for cls in _getAvailableFiltes():
        name = cls.__doc__
        menu.addAction(name, setFilter(varWrapper, cls))


class Empty:
    """None (remove filter)"""
    @staticmethod
    def toDisplay(val):
        return val

    @staticmethod
    def fromDisplay(val):
        return val


class Hex(Empty):
    """Hex"""
    @staticmethod
    def toDisplay(val):
        return hex(int(val))

    @staticmethod
    def fromDisplay(val):
        return int(val, 16)


class Bin(Empty):
    """Bin"""
    @staticmethod
    def toDisplay(val):
        return bin(int(val))

    @staticmethod
    def fromDisplay(val):
        return int(val, 2)
