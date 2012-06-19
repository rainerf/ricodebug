from PyQt4.QtCore import Qt
from PyQt4 import QtGui

# plugin requirements:
#  - plugin must be a package inside folder "plugins"
#  - package must contain one file ending with "Plugin.py" (e.g. SamplePlugin.py)
#  - this file must contain a class named like the file (e.g. SamplePlugin)
#  - this class must implement the functions initPlugin(signalproxy) and deInitPlugin() to load/unload plugin
#
# The variable PluginName in the __init__.py file of each package may be used to define a name for the plugin


class SamplePlugin():
    ''' Sample plugin Widget '''

    # =================================
    # functions called by pluginloader
    # =================================
    def __init__(self):
        self.dockwidget = None

    def initPlugin(self, signalproxy):
        """Init function - called when pluginloader loads plugin."""

        self.signalproxy = signalproxy

        qwidget = QtGui.QWidget()
        qlayout = QtGui.QHBoxLayout()
        qlabel = QtGui.QLabel("This is a sample plugin widget")
        qlayout.addWidget(qlabel)
        qwidget.setLayout(qlayout)

        # create and place DockWidget in mainwindow using signalproxy
        self.signalproxy.insertDockWidget(self, qwidget, "Sample", Qt.BottomDockWidgetArea, True)

    def deInitPlugin(self):
        """Deinit function - called when pluginloader unloads plugin."""
        self.signalproxy.removeDockWidget(self)
