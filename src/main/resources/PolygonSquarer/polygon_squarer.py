# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonSquarer
                                 A QGIS plugin
 Least square algorithm
                              -------------------
        begin                : 2018-05-22
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Imran
        email                : imran.lokhat@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QProcess
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from polygon_squarer_dialog import PolygonSquarerDialog
import os.path
import StringIO
import configparser


class PolygonSquarer:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PolygonSquarer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Polygon Squarer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PolygonSquarer')
        self.toolbar.setObjectName(u'PolygonSquarer')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PolygonSquarer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = PolygonSquarerDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PolygonSquarer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Square polygons'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Polygon Squarer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def select_output_file(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Select conf file ","", '*.conf')
        self.dlg.lineEdit.setText(filename)

    def getLayers(self):
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)
        return layers

    def buildCommandLine(self, pluginPath, confFile, inputFile, outputFile, jPath):
        jarName = 'polysquarer.jar'
        javaPath = 'java'
        if os.name == "nt":
                javaPath = jPath + '/' + javaPath
        cmds = []
        cmds.append(javaPath)
        cmds.append("-jar")
        cmds.append(pluginPath + '/' + jarName)
        cmds.append(confFile)
        cmds.append(inputFile)
        cmd = " ".join(cmds)
        return cmd

    def sanitizePath(self, strPipe):
        pipe_pos = strPipe.index('|')
        return strPipe[:pipe_pos]

    def buildCorrectIniFile(self, confFile):
        config = configparser.ConfigParser()
        with open(confFile, 'r') as f:
            cf = '[section]\n' + f.read()
        cfini = StringIO.StringIO(cf)
        config.readfp(cfini)
        return config


    def run(self):
        """Run method that performs all the real work"""
        plugin_path = os.path.dirname(os.path.realpath(__file__))
        layers = self.getLayers()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            confFile = self.dlg.lineEdit.text()
            config = self.buildCorrectIniFile(confFile)
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
            layerPath = self.sanitizePath(selectedLayer.dataProvider().dataSourceUri())
            outputPath = config.get('section', 'outputShape')
            timeout = float(config.get('section', 'timeout_secs')) * 1000
            cmd = self.buildCommandLine(plugin_path, confFile, layerPath, outputPath)
            print cmd
            process = QProcess(self.iface)
            process.start(cmd)
            process.waitForFinished(timeout)
            resLayer = QgsVectorLayer(outputPath, "result", "ogr")
            QgsMapLayerRegistry.instance().addMapLayers([resLayer,], True)
            process.kill()
