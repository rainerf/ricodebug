from lib.formlayout import fedit
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QObject


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


class Separator:
    def __init__(self, context, name):
        context.appendConfigItem(self)
        self.description = None
        self.value = name


class ConfigSet(QObject):
    itemsHaveChanged = pyqtSignal()

    def __init__(self, name, comment):
        QObject.__init__(self)
        self._name = name
        self._comment = comment
        self.items = []
        self.__itemHasChanged = False

    def getConfigTuple(self):
        return ([(v.description, v.value) for v in self.items], self._name, self._comment)

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
                        i.value = settings.value(desc).toBool()
                    elif isinstance(i._default, basestring):
                        i.value = str(settings.value(desc).toString())
                    elif isinstance(i._default, int):
                        i.value = int(settings.value(desc).toInt()[0])
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
