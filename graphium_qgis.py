# -*- coding: utf-8 -*-

"""
/***************************************************************************
 QGIS plugin 'Graphium'
/***************************************************************************
 *
 * Copyright 2020 Simon Gröchenig @ Salzburg Research
 * eMail     graphium@salzburgresearch.at
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ***************************************************************************/
"""

import os.path
from PyQt5.QtCore import (QTranslator, QCoreApplication)
from PyQt5.QtGui import (QIcon)
from PyQt5 import (QtWidgets)
# QGIS imports
from processing.tools.general import *
from qgis import processing
# Graphium imports
from .graphium.graph_management.graphium_qgis_graphmanager import GraphiumQGISGraphManager
from .graphium.settings import Settings
from .graphium.graphium_processing_provider import GraphiumProcessingProvider


class GraphiumQGIS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GraphiumQGIS_{}.qm'.format(Settings.get_locale()))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Graphium Tools')

        self.toolbar = self.iface.addToolBar(u'Graphium Tools')
        self.toolbar.setObjectName(u'Graphium Tools')

        # processes
        self.provider = GraphiumProcessingProvider()

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
        return QCoreApplication.translate('Graphium Tools', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
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
        # self.dlg = GraphiumQGISDialog()

        icon = QIcon(icon_path)
        action = QtWidgets.QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # https://github.com/jdugge/BufferByPercentage/blob/master/bufferbypercentage.py
        plugin_path = os.path.dirname(__file__)

        self.add_action(
            os.path.join(plugin_path, 'icons/icon.svg'),
            text=self.tr(u'Graphium Manager'),
            callback=self.run_graph_manager,
            parent=None)
        self.add_action(
            os.path.join(plugin_path, 'icons/icon_map_matcher.svg'),
            text=self.tr(u'Map Matcher'),
            callback=self.run_mapmatcher,
            parent=None)
        self.add_action(
            os.path.join(plugin_path, 'icons/icon_routing.svg'),
            text=self.tr(u'Routing'),
            callback=self.run_routing,
            parent=None)
        self.add_action(
            os.path.join(plugin_path, 'icons/icon.svg'),
            text=self.tr(u'OSM 2 Graphium Converter'),
            callback=self.run_osm2graphium,
            add_to_toolbar=False,
            parent=None)
        self.add_action(
            os.path.join(plugin_path, 'icons/icon.svg'),
            text=self.tr(u'GIP 2 Graphium Converter'),
            callback=self.run_gip2graphium,
            add_to_toolbar=False,
            parent=None)

        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        # remove provider
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run_graph_manager(self):
        graph_manager = GraphiumQGISGraphManager(self.iface)
        graph_manager.run()

    def run_mapmatcher(self):
        # https://github.com/qgis/QGIS/blob/master/python/plugins/processing/tools/general.py
        processing.execAlgorithmDialog("Graphium:mapmatcher")

    def run_routing(self):
        processing.execAlgorithmDialog("Graphium:routing")

    def run_osm2graphium(self):
        processing.execAlgorithmDialog("Graphium:osm2graphiumconverter")

    def run_gip2graphium(self):
        processing.execAlgorithmDialog("Graphium:gip2graphiumconverter")

    def run(self):
        """Run method that performs all the real work"""
        pass
        # # show the dialog
        # self.dlg.show()
        # # Run the dialog event loop
        # result = self.dlg.exec_()
        # # See if OK was pressed
        # if result:
        #     pass
        #     # self.do_map_matching()
        #     # self.do_routing()
