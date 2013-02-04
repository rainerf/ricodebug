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

from .datagraphvw import HtmlTemplateHandler, DataGraphVW
from .htmlvariableview import HtmlVariableView


class SVGDataGraphVW(DataGraphVW):
    """ Wrapper for SVG Images """

    def __init__(self, image, distributedObjects):
        """ Constructor
        @param image               SVG image to wrap with the new DataGraphVW
        @param distributedObjects  the DistributedObjects-Instance
        """
        DataGraphVW.__init__(self, image, distributedObjects)
        self.image = image
        self.templateHandler = HtmlTemplateHandler(self,
                                                   self.distributedObjects,
                                                   "svgview.mako")

    def showContent(self):
        self.image.refresh()
        return self.image.imageContent

    def showName(self):
        return str(self.image)

    def render(self, role, **kwargs):
        return self.templateHandler.render(role)

    def createView(self):
        self._view = HtmlVariableView(self, self.distributedObjects)
        self.parentWrapper = self._view
