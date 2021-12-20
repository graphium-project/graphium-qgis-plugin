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
from PyQt5.QtCore import QTranslator, QCoreApplication
from PyQt5 import QtWidgets
# qgis
from qgis.core import Qgis
# Import the code for the dialog
from .graphium_qgis_graph_select_dialog import GraphiumQGISGraphSelectDialog
# plugin classes
from Graphium.graphium.graphium_graph_management_api import GraphiumGraphManagementApi
from Graphium.graphium.connection.graphium_connection_manager import GraphiumConnectionManager
from Graphium.graphium.settings import Settings


class GraphiumQGISGraphSelect:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, filter_server_type=None, filter_version_state=None, select_version=False):
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
            'graphium_qgis_{}.qm'.format(Settings.get_locale()))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GraphiumQGISGraphSelectDialog()

        self.dlg.btnConnect.clicked.connect(self.graph_server_changed)

        self.filter_server_type = filter_server_type
        self.filter_version_state = filter_version_state
        self.select_version = select_version

        # graphium
        self.graphium = GraphiumGraphManagementApi()
        self.connection_manager = GraphiumConnectionManager()
        self.graph_names = []
        self.graph_versions = []

        if select_version:
            self.dlg.groupGraphVersion.setEnabled(True)
        else:
            self.dlg.groupGraphVersion.setEnabled(False)

        self.selected_connection = None
        self.selected_graph_name = None
        self.selected_graph_version = None

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
        return QCoreApplication.translate('GraphiumQGIS', message)

    def get_connections(self):
        # read input
        self.connection_manager.read_connections(self.filter_server_type)
        # prepare connection combo box
        cbo_connection_items = list()
        for conn in self.connection_manager.connections:
            cbo_connection_items.append(conn.name + ' [' + conn.get_connection_url() + ']')
        self.dlg.cboConnections.clear()
        self.dlg.cboConnections.addItems(cbo_connection_items)

    def connect_to_graphium(self):
        if self.dlg.cboConnections.count() == 0:
            self.iface.messageBar().pushMessage("Warning", "No Graphium server selected", level=Qgis.Critical)
            return

        self.dlg.btnConnect.setEnabled(False)
        selected_connection_index = self.dlg.cboConnections.currentIndex()
        selected_connection = self.connection_manager.connections[selected_connection_index]
        if self.graphium.connect(selected_connection):
            self.import_graph_names()
            self.import_graph_versions()

            self.dlg.cboGraphNames.setEnabled(True)
            if self.select_version:
                self.dlg.cboGraphVersions.setEnabled(True)
        else:
            self.iface.messageBar().pushMessage("Warning", "Cannot connect to Graphium server [" +
                                                selected_connection.name + "]", level=Qgis.Critical, duration=5)
            self.dlg.cboGraphNames.setEnabled(False)
            self.dlg.cboGraphVersions.setEnabled(False)
        self.dlg.btnConnect.setEnabled(True)

    def import_graph_names(self):
        self.graph_names = self.graphium.get_graph_names()
        name_list = list()

        selected_graph_name = Settings.get_selected_graph_name()
        current_index = 0
        i = 0
        for n in self.graph_names:
            name_list.append(n)
            if isinstance(selected_graph_name, str) and selected_graph_name == n:
                current_index = i
            i += 1
        self.dlg.cboGraphNames.clear()
        self.dlg.cboGraphNames.addItems(name_list)
        self.dlg.cboGraphNames.setCurrentIndex(current_index)

    def import_graph_versions(self):
        if len(self.graph_names) == 0:
            return

        selected_name_index = self.dlg.cboGraphNames.currentIndex()
        selected_name = self.graph_names[selected_name_index]

        self.graph_versions = self.graphium.get_graph_versions(selected_name, state_filter=self.filter_version_state)
        version_list = list()

        selected_graph_version = Settings.get_selected_graph_version()
        current_index = 0
        i = 0
        for v in self.graph_versions:
            version_list.append(v['version'] + ' (' + v['state'] + ')')
            if isinstance(selected_graph_version, str) and selected_graph_version == v:
                current_index = i
            i += 1
        self.dlg.cboGraphVersions.clear()
        self.dlg.cboGraphVersions.addItems(version_list)
        self.dlg.cboGraphVersions.setCurrentIndex(current_index)

    def graph_server_changed(self):
        self.connect_to_graphium()

    def graph_name_changed(self):
        self.import_graph_versions()

    def graph_version_changed(self):
        pass

    def run(self):
        """Run method that performs all the real work"""
        self.get_connections()

        self.dlg.cboGraphNames.clear()
        self.dlg.cboGraphVersions.clear()

        self.dlg.cboGraphNames.setEnabled(False)
        self.dlg.cboGraphVersions.setEnabled(False)

        self.dlg.cboGraphNames.currentIndexChanged['QString'].connect(self.graph_name_changed)
        self.dlg.cboGraphVersions.currentIndexChanged['QString'].connect(self.graph_version_changed)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            if self.dlg.cboConnections.count() > 0:
                selected_connection_index = self.dlg.cboConnections.currentIndex()
                self.selected_connection = self.connection_manager.connections[selected_connection_index]
            else:
                return False

            if self.dlg.cboGraphNames.count() > 0:
                selected_name_index = self.dlg.cboGraphNames.currentIndex()
                self.selected_graph_name = self.graph_names[selected_name_index]
            else:
                return False

            if self.dlg.cboGraphVersions.count() > 0:
                selected_version_index = self.dlg.cboGraphVersions.currentIndex()
                self.selected_graph_version = self.graph_versions[selected_version_index]
            else:
                return False

        return result
