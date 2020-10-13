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
from datetime import datetime
import threading
# PyQt imports
from qgis.PyQt.QtCore import (QTranslator, QCoreApplication, Qt)
from qgis.PyQt.QtWidgets import (QMenu, QMessageBox)
# qgis imports
from qgis.core import Qgis, QgsProcessingException
from qgis import processing
# Import the code for the dialog
from .graphium_qgis_graphmanager_dialog import GraphiumQGISGraphManagerDialog
# Graphium imports
from ..connection.graphium_qgis_connection import GraphiumQGISConnectionManager
# plugin classes
from ..graphium_graph_management_api import GraphiumGraphManagementApi
from ..connection.model.graphium_connection import Connection
from ..connection.graphium_connection_manager import GraphiumConnectionManager
from .algorithm.activate_graph_version_algorithm import (ActivateGraphVersionAlgorithm)
from .algorithm.add_graph_version_algorithm import (AddGraphVersionAlgorithm)
from .algorithm.remove_graph_version_algorithm import (RemoveGraphVersionAlgorithm)
from .algorithm.update_graph_version_attribute_algorithm import (UpdateGraphVersionAttributeAlgorithm)
from ..graph_data.algorithm.download_graph_version_algorithm import (DownloadGraphVersionAlgorithm)
from .model.table_graph_version import TableGraphVersionModel
from .model.table_graph_name import TableGraphNameModel
from ..settings import Settings


class GraphiumQGISGraphManager:
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
            'graphium_qgis_{}.qm'.format(Settings.get_locale()))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # graphium
        self.graphium = GraphiumGraphManagementApi()
        self.connection_manager = GraphiumConnectionManager()
        self.selected_connection = None
        self.settings = Settings()
        self.graph_names = []
        self.table_graph_names_data = []
        self.graph_versions = []

        # Create the dialog (after translation) and keep reference
        self.dlg = GraphiumQGISGraphManagerDialog(parent=self.iface.mainWindow())

        self.dlg.btnConnect.clicked.connect(self.connect_to_graphium)
        self.dlg.btnNewConnection.clicked.connect(self.new_connection)
        self.dlg.btnEditConnection.clicked.connect(self.edit_connection)
        self.dlg.btnRemoveConnection.clicked.connect(self.remove_connection)

        self.switch_to_graph_name_view()

        self.dlg.btnRefreshGraphNames.clicked.connect(self.switch_to_graph_name_view)
        self.dlg.btnManageSelectedGraphName.clicked.connect(self.switch_to_graph_version_view)
        self.dlg.tableGraphNames.doubleClicked .connect(self.switch_to_graph_version_view)

        self.dlg.btnHideGraphVersions.clicked.connect(self.switch_to_graph_name_view)
        self.dlg.btnRefreshGraphVersions.clicked.connect(self.switch_to_graph_version_view)
        self.dlg.btnSetDefaultGraphVersion.clicked.connect(self.set_default_graph_version)

        add_graph_name_menu = QMenu()
        add_graph_name_menu.addAction('Add ...', self.add_graph_version)
        add_graph_name_menu.addAction('Add from OSM', self.add_graph_version_from_osm)
        add_graph_name_menu.addAction('Add from GIP', self.add_graph_version_from_gip)
        self.dlg.btnAddGraphName.setMenu(add_graph_name_menu)
        self.dlg.btnAddGraphVersion.setMenu(add_graph_name_menu)

        self.dlg.btnActivateGraphVersion.clicked.connect(self.activate_graph_version)
        self.dlg.btnDownloadGraphVersion.clicked.connect(self.download_graph_version_to_map)
        self.dlg.btnDeleteGraphVersion.clicked.connect(self.remove_graph_version)

        self.dlg.chkFilterStateInitial.setChecked(True)
        self.dlg.chkFilterStateActive.setChecked(True)
        self.dlg.chkFilterStateDeleted.setChecked(False)

        self.dlg.chkFilterStateInitial.toggled.connect(self.switch_to_graph_version_view)
        self.dlg.chkFilterStateActive.toggled.connect(self.switch_to_graph_version_view)
        self.dlg.chkFilterStateDeleted.toggled.connect(self.switch_to_graph_version_view)

        self.dlg.lblDefaultGraphiumServer.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.dlg.lblDefaultGraphName.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.dlg.lblDefaultGraphVersion.setTextInteractionFlags(Qt.TextSelectableByMouse)

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

    def read_connections(self, selected_index=-1):
        # read connections and prepare connection combo box
        cbo_connection_items = list()
        selected_graph_server = Settings.get_selected_graph_server()
        for index, conn in enumerate(self.connection_manager.read_connections()):
            cbo_connection_items.append(conn.name + ' (' + conn.get_connection_url() + ')')
            if selected_index == -1 and isinstance(selected_graph_server, str) and conn.name == selected_graph_server:
                selected_index = index
        self.dlg.cboConnections.clear()
        self.dlg.cboConnections.addItems(cbo_connection_items)
        if selected_index != -1:
            self.dlg.cboConnections.setCurrentIndex(selected_index)

    def open_connection_editor(self, connection):
        connection_manager = GraphiumQGISConnectionManager(self.iface, connection)
        if connection_manager.run():
            return True
        else:
            return False

    def new_connection(self):
        selected_connection_index = self.dlg.cboConnections.currentIndex()
        new_connection = Connection()
        if self.open_connection_editor(new_connection):
            self.connection_manager.connections.append(new_connection)
            selected_connection_index = len(self.connection_manager.connections) - 1
        self.connection_manager.save_connections()
        self.read_connections(selected_connection_index)

    def edit_connection(self):
        selected_connection_index = self.dlg.cboConnections.currentIndex()
        selected_connection = self.connection_manager.connections[selected_connection_index]
        self.open_connection_editor(selected_connection)
        self.connection_manager.save_connections()
        self.read_connections(selected_connection_index)

    def remove_connection(self):
        reply = QMessageBox.question(self.dlg, 'Graphium', 'Do you really want to REMOVE the selected connection?',
                                               QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            selected_connection_index = self.dlg.cboConnections.currentIndex()
            del self.connection_manager.connections[selected_connection_index]
            self.connection_manager.save_connections()
            self.read_connections()

    def connect_to_graphium(self):
        if self.dlg.cboConnections.count() == 0:
            self.iface.messageBar().pushMessage("Graphium", "No Graphium server selected", level=Qgis.Critical)
            return

        selected_connection_index = self.dlg.cboConnections.currentIndex()
        self.selected_connection = self.connection_manager.connections[selected_connection_index]

        if self.graphium.connect(self.selected_connection):
            self.iface.messageBar().pushSuccess("Graphium", "Connected to Graphium server [" +
                                                self.selected_connection.name + "]")
        else:
            self.iface.messageBar().pushMessage("Graphium", "Cannot connect to Graphium server [" +
                                                self.selected_connection.name + "]", level=Qgis.Warning)
            self.selected_connection = None

        self.switch_to_graph_name_view()

    def switch_to_graph_name_view(self):
        """
        Reads the versions of the selected graph name and updates the graph version table in dialog
        :return:
        """

        self.dlg.widgetGraphNames.show()
        self.dlg.widgetGraphVersions.hide()

        if self.selected_connection:
            self.dlg.widgetGraphNames.setEnabled(True)
            self.dlg.lblConnectedGraphServer.setText('Connected server: ' + self.selected_connection.name)
        else:
            self.dlg.widgetGraphNames.setEnabled(False)
            self.dlg.lblConnectedGraphServer.setText('Connected server: None')

        self.graph_names = []
        if self.selected_connection:
            response = self.graphium.get_graph_names()
            if not 'error' in response:
                self.graph_names = response
            else:
                self.iface.messageBar().pushMessage("Graphium", "Cannot retrieve graphs from Graphium server [" +
                                                    self.selected_connection.name + "], Reason: " +
                                                    response['error']['msg'], level=Qgis.Warning)

        default_graph_name = Settings.get_selected_graph_name()
        default_graph_name_index = -1

        self.graph_names = sorted(self.graph_names)

        self.table_graph_names_data = list()
        for index, graph_name in enumerate(self.graph_names):
            self.table_graph_names_data.append({
                'name': graph_name,
                'graph_version_count': None
            })
            if graph_name == default_graph_name:
                default_graph_name_index = index

        threads = []
        for index, graph_name in enumerate(self.graph_names):
            t = threading.Thread(target=self.get_number_of_graph_versions, args=(index,),
                                 daemon=True)
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        # create the view
        table_view = self.dlg.tableGraphNames

        # set the table model
        header = ['Graph name', 'Graph version count']
        tm = TableGraphNameModel(self.table_graph_names_data, header)
        tm.default_graph_name_index = default_graph_name_index
        table_view.setModel(tm)

        # show grid
        table_view.setShowGrid(True)
        # hide vertical header
        vertical_header = table_view.verticalHeader()
        vertical_header.setVisible(False)
        # set horizontal header properties
        horizontal_header = table_view.horizontalHeader()
        horizontal_header.setVisible(True)
        # horizontal_header.setStretchLastSection(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        for row in range(len(self.table_graph_names_data)):
            table_view.setRowHeight(row, 20)
        # disable sorting
        table_view.setSortingEnabled(False)

    def get_number_of_graph_versions(self, graphname_index):
        response = self.graphium.get_graph_versions(self.table_graph_names_data[graphname_index]['name'])
        if 'error' in response:
            self.table_graph_names_data[graphname_index]['graph_version_count'] = 0
        else:
            self.table_graph_names_data[graphname_index]['graph_version_count'] = len(response)

    def switch_to_graph_version_view(self):
        """
        Reads the versions of the selected graph name and updates the graph version table in dialog
        :return:
        """

        selected_graph_name = self.get_selected_graph_name()
        if selected_graph_name is None:
            self.iface.messageBar().pushMessage('No graph name selected...')
            self.switch_to_graph_name_view()
            return

        self.dlg.widgetGraphNames.hide()
        self.dlg.widgetGraphVersions.show()
        self.dlg.lblSelectedGraphName.setText('Selected graph name: ' + selected_graph_name)

        response = self.graphium.get_graph_versions(selected_graph_name)
        if 'error' in response:
            self.iface.messageBar().pushMessage("Graphium", "Cannot retrieve graph versions from Graphium server [" +
                                                self.selected_connection.name + "]", level=Qgis.Warning)
            self.graph_versions = []
        else:
            self.graph_versions = response

        if not self.dlg.chkFilterStateInitial.isChecked():
            self.graph_versions = list(filter(lambda v: v.get('state') != 'INITIAL', self.graph_versions))
        if not self.dlg.chkFilterStateActive.isChecked():
            self.graph_versions = list(filter(lambda v: v.get('state') != 'ACTIVE', self.graph_versions))
        if not self.dlg.chkFilterStateDeleted.isChecked():
            self.graph_versions = list(filter(lambda v: v.get('state') != 'DELETED', self.graph_versions))

        self.graph_versions = sorted(self.graph_versions, key=lambda entry: entry['validFrom'])

        default_graph_version = Settings.get_selected_graph_version()
        default_graph_version_index = -1

        table_data = list()
        for index, version in enumerate(self.graph_versions):
            valid_from = datetime.utcfromtimestamp(version.get('validFrom', 0) / 1000) if 'validFrom' in version else \
                None
            valid_to = datetime.utcfromtimestamp(version.get('validTo', 0) / 1000) if 'validTo' in version else None

            table_data.append({'id': version.get('id', ""),
                               'version': version.get('version'),
                               'type': 'HD' if version.get('type', '') == 'hdwaysegment' else '',
                               'state': version.get('state'),
                               'validFrom': valid_from,
                               'validTo': valid_to})
            if version['version'] == default_graph_version:
                default_graph_version_index = index

        # create the view
        table_view = self.dlg.tableGraphVersions

        # set the table model
        header = ['ID', 'Graph version', 'Type', 'State', 'Valid From', 'Valid To']
        tm = TableGraphVersionModel(table_data, header, self.update_graph_version_validity, self)
        tm.default_graph_version_index = default_graph_version_index
        table_view.setModel(tm)

        # # https://gist.github.com/Riateche/5984815
        # for row in range(0, tm.rowCount()):
        #     table_view.openPersistentEditor(tm.index(row, 3))

        # show grid
        table_view.setShowGrid(True)
        # hide vertical header
        vertical_header = table_view.verticalHeader()
        vertical_header.setVisible(False)
        # set horizontal header properties
        horizontal_header = table_view.horizontalHeader()
        horizontal_header.setVisible(True)
        # horizontal_header.setStretchLastSection(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        for row in range(len(table_data)):
            table_view.setRowHeight(row, 20)
        # disable sorting
        table_view.setSortingEnabled(False)

    def add_graph_version(self):
        """
        Opens an algorithm dialog to add a new graph version
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version(False)

        parameters = {
            AddGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex(),
            AddGraphVersionAlgorithm.GRAPH_NAME: graph_name if graph_name else '',
            AddGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version'] if graph_version else '',
            AddGraphVersionAlgorithm.OVERRIDE_IF_EXISTS: False
        }

        processing.execAlgorithmDialog("Graphium:AddGraphVersion", parameters)

        # update ui
        self.switch_to_graph_version_view()

    def add_graph_version_from_osm(self):
        """
        Opens an algorithm dialog to add a new graph version from a GIP data source
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version(False)

        parameters = {
            AddGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex() + 1,
            AddGraphVersionAlgorithm.GRAPH_NAME: graph_name if graph_name else '',
            AddGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version'] if graph_version else '',
            AddGraphVersionAlgorithm.OVERRIDE_IF_EXISTS: False
        }

        processing.execAlgorithmDialog("Graphium:osm2graphiumconverter", parameters)

        # update ui
        self.switch_to_graph_version_view()

    def add_graph_version_from_gip(self):
        """
        Opens an algorithm dialog to add a new graph version from a GIP data source
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version(False)

        parameters = {
            AddGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex() + 1,
            AddGraphVersionAlgorithm.GRAPH_NAME: graph_name if graph_name else '',
            AddGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version'] if graph_version else '',
            AddGraphVersionAlgorithm.OVERRIDE_IF_EXISTS: False
        }

        processing.execAlgorithmDialog("Graphium:gip2graphiumconverter", parameters)

        # update ui
        self.switch_to_graph_version_view()

    def remove_graph_version(self):
        """
        Calls an algorithm to delete the selected graph version
        :return:
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version()
        if graph_version is None:
            return

        if graph_version['state'] != 'DELETED':
            reply = QMessageBox.question(self.dlg, 'Graphium',
                                                   'Do you really want to REMOVE the selected graph version?',
                                                   QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                parameters = {
                    RemoveGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex(),
                    RemoveGraphVersionAlgorithm.GRAPH_NAME: graph_name,
                    RemoveGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version']
                }

                try:
                    processing.execAlgorithmDialog("Graphium:RemoveGraphVersion", parameters)
                except QgsProcessingException:
                    self.iface.messageBar().pushMessage("Warning", "Could not remove graph version",
                                                        level=Qgis.Critical)

                # update ui
                self.switch_to_graph_version_view()

        else:
            self.iface.messageBar().pushMessage("Warning", "Cannot remove graph version with state [DELETED]",
                                                level=Qgis.Warning)

    def activate_graph_version(self):
        """
        Calls an algorithm to activate the selected graph version
        :return:
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version()
        if graph_version is None:
            return

        if graph_version['state'] == 'INITIAL':
            reply = QMessageBox.question(self.dlg,
                                                   'Graphium',
                                                   'Do you really want to ACTIVATE the selected graph version?',
                                                   QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                parameters = {
                        ActivateGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex(),
                        ActivateGraphVersionAlgorithm.GRAPH_NAME: graph_name,
                        ActivateGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version']
                    }

                try:
                    processing.execAlgorithmDialog("Graphium:ActivateGraphVersion", parameters)
                except QgsProcessingException:
                    self.iface.messageBar().pushMessage("Warning", "Could not activate graph version",
                                                        level=Qgis.Critical)

                # update ui
                self.switch_to_graph_version_view()
        else:
            self.iface.messageBar().pushMessage("Warning", "Cannot activate graph version with state [" +
                                                graph_version['state'] + "]", level=Qgis.Warning)

    def update_graph_version_validity(self, graph_version, attribute, valid_date):
        selected_name = self.get_selected_graph_name()

        parameters = {
            UpdateGraphVersionAttributeAlgorithm.SERVER_NAME: self.selected_connection.name,
            UpdateGraphVersionAttributeAlgorithm.GRAPH_NAME: selected_name,
            UpdateGraphVersionAttributeAlgorithm.GRAPH_VERSION: graph_version,
            UpdateGraphVersionAttributeAlgorithm.ATTRIBUTE: 0 if attribute == 'validFrom' else 1,
            UpdateGraphVersionAttributeAlgorithm.NEW_VALUE: valid_date
        }

        try:
            processing.execAlgorithmDialog("Graphium:UpdateGraphVersionValidity", parameters)
        except QgsProcessingException:
            self.iface.messageBar().pushMessage("Warning", "Could not update graph version validity",
                                                level=Qgis.Critical)

        # update ui
        self.switch_to_graph_version_view()

    def download_graph_version_to_map(self):
        """
        Calls an algorithm to download the selected graph version
        :return:
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version()
        if graph_version is None:
            return

        parameters = {
                DownloadGraphVersionAlgorithm.SERVER_NAME: self.dlg.cboConnections.currentIndex(),
                DownloadGraphVersionAlgorithm.GRAPH_NAME: graph_name,
                DownloadGraphVersionAlgorithm.GRAPH_VERSION: graph_version['version']
            }

        if self.settings.is_hd_enabled():
            parameters[DownloadGraphVersionAlgorithm.HD_WAYSEGMENTS] =\
                True if graph_version.get('type', '') == 'hdwaysegment' else False

        try:
            processing.execAlgorithmDialog("Graphium:DownloadGraphVersion", parameters)
        except QgsProcessingException:
            self.iface.messageBar().pushMessage("Warning", "Could not download the selected graph version",
                                                level=Qgis.Critical)

    def set_default_graph_version(self):
        """
        Sets default server, graph name and graph version
        :return:
        """
        graph_name, graph_version = self.get_selected_graph_name_and_version()
        if graph_name is None:
            self.iface.messageBar().pushMessage("Warning", "No graph name selected!")
            return
        if graph_version is None:
            self.iface.messageBar().pushMessage("Warning", "No graph version selected!")
            return

        Settings.set_selected_graph_version(self.selected_connection.name, graph_name, graph_version['version'])

        # update ui
        self.switch_to_graph_version_view()
        self.set_default_graph()

    def get_selected_graph_name(self):
        """
        Retrieves the selected graph name from the dialog
        :return: selected_graph_name
        """
        selected_graph_name = None
        if self.dlg.tableGraphNames.selectionModel():
            selected_name_indexes = self.dlg.tableGraphNames.selectionModel().selectedRows()
            if len(selected_name_indexes) == 1:
                selected_graph_name = self.graph_names[selected_name_indexes[0].row()]

        return selected_graph_name

    def get_selected_graph_name_and_version(self, push_messages=True):
        """
        Retrieves the selected graph name and version from the dialog
        :return: selected_graph_name, selected_graph_version
        """
        selected_graph_name = self.get_selected_graph_name()

        selected_graph_version = None
        if self.dlg.tableGraphVersions.selectionModel():
            selected_version_indexes = self.dlg.tableGraphVersions.selectionModel().selectedRows()
            if len(selected_version_indexes) == 1:
                selected_graph_version = self.graph_versions[selected_version_indexes[0].row()]

        if selected_graph_version is None:
            if push_messages:
                self.iface.messageBar().pushMessage("Warning", "No graph version selected", level=Qgis.Warning)
            return selected_graph_name, None

        return selected_graph_name, selected_graph_version

    def set_default_graph(self):
        s = Settings.get_selected_graph_server()
        connection = None
        if isinstance(s, str):
            self.connection_manager.read_connections(None)
            for conn in self.connection_manager.connections:
                if conn.name == s:
                    connection = conn
        if connection is not None:
            self.dlg.lblDefaultGraphiumServer.setText(connection.name + ' [' +
                                                      connection.get_connection_url() + ']')
        else:
            self.dlg.lblDefaultGraphiumServer.setText(self.tr('Graph server not set'))

        s = Settings.get_selected_graph_name()
        if isinstance(s, str):
            self.dlg.lblDefaultGraphName.setText(s)
        else:
            self.dlg.lblDefaultGraphName.setText('No default graph name set!')
        s = Settings.get_selected_graph_version()
        if isinstance(s, str):
            self.dlg.lblDefaultGraphVersion.setText(s)
        else:
            self.dlg.lblDefaultGraphVersion.setText('No default graph version set!')

        if connection:
            self.dlg.lblServerStatus.setText('Check connection')
            check_server_thread = threading.Thread(target=self.check_server, args=(connection,), daemon=True)
            check_server_thread.start()

    def check_server(self, connection):
        graphium_for_check = GraphiumGraphManagementApi()
        if graphium_for_check.connect(connection) is False:
            self.dlg.lblServerStatus.setText('Server does not respond!')
        else:
            self.dlg.lblServerStatus.setText('Server is listening...')
        graphium_for_check.disconnect()

    def run(self):
        self.set_default_graph()

        self.read_connections()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        return self.dlg.exec_()
