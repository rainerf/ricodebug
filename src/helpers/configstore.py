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

from PyQt4.QtCore import pyqtSignal, pyqtSlot, QObject

from lib.formlayout import fedit
import logging


class ConfigItem(QObject):
    valueChanged = pyqtSignal('PyQt_PyObject')

    def __init__(self, context, desc, default, value=None):
        QObject.__init__(self)
        self.context = context
        self.context.appendConfigItem(self)
        self.description = desc
        self._default = default
        self._value = value

    def getValue(self):
        return self._value if self._value is not None else self._default

    def setValue(self, value):
        if value != self.value:
            self._value = value
            self.valueChanged.emit(self._value)
    value = property(getValue, setValue)

    def getConfigTuple(self):
        return (self.description, self.value)


class SelectionConfigItem(ConfigItem):
    def __init__(self, context, desc, default, values, value=None):
        ConfigItem.__init__(self, context, desc, default, value)
        self.values = values
        if self._default not in self.values:
            raise ValueError("Default value '%s' not allowed" % self._default)

    def setValue(self, value):
        if value not in self.values:
            raise ValueError("Value '%s' not allowed" % value)
        ConfigItem.setValue(self, value)
    value = property(ConfigItem.getValue, setValue)

    def getConfigTuple(self):
        l = [self.value]
        l.extend(self.values)
        return (self.description, l)


class Separator:
    def __init__(self, context, name):
        context.appendConfigItem(self)
        self.name = name

    def getConfigTuple(self):
        return (None, self.name)


class ConfigSet(QObject):
    itemsHaveChanged = pyqtSignal()

    def __init__(self, name, comment, icon=None):
        QObject.__init__(self)
        self._name = name
        self._comment = comment
        self._icon = icon
        self.items = []
        self.__itemHasChanged = False

    def getConfigTuple(self):
        return ([v.getConfigTuple() for v in self.items], self._name, self._comment, self._icon)

    def appendConfigItem(self, i):
        self.items.append(i)
        if isinstance(i, ConfigItem):
            i.valueChanged.connect(self.itemChanged)

    def beginUpdateItems(self):
        self.__itemHasChanged = False

    @pyqtSlot()
    def itemChanged(self):
        self.__itemHasChanged = True

    def endUpdateItems(self, settings):
        if self.__itemHasChanged:
            self.itemsHaveChanged.emit()
            self.__storeSettings(settings)

    def __storeSettings(self, settings):
        settings.beginGroup(self._name)
        for i in self.items:
            if isinstance(i, ConfigItem):
                settings.setValue(i.description.lower(), i.value)
        settings.endGroup()

    def loadSettings(self, settings):
        settings.beginGroup(self._name)
        for i in self.items:
            if isinstance(i, ConfigItem):
                desc = i.description.lower()
                if settings.contains(desc):
                    # use the item's default value to check the type we should read
                    if isinstance(i._default, bool):
                        try:
                            i.value = {"true": True, "false": False}[settings.value(desc)]
                        except KeyError:
                            logging.error("Illegal value %s for boolean key %s/%s in settings, using default value.", settings.value(desc), self._name, desc)
                    elif isinstance(i._default, str):
                        i.value = str(settings.value(desc))
                    elif isinstance(i._default, int):
                        i.value = int(settings.value(desc))
        settings.endGroup()


class ConfigStore:
    def __init__(self, settings):
        self.datasets = []
        self.__settings = settings

    def registerConfigSet(self, cs):
        self.datasets.append(cs)
        cs.loadSettings(self.__settings)

    @pyqtSlot()
    def edit(self):
        resultlists = fedit([l.getConfigTuple() for l in self.datasets])
        if resultlists:
            for configset, resultlist in zip(self.datasets, resultlists):
                configset.beginUpdateItems()
                for config, result in zip((c for c in configset.items if isinstance(c, ConfigItem)), resultlist):
                    config.value = result
                configset.endUpdateItems(self.__settings)
