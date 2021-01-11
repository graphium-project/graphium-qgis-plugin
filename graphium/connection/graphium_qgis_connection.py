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
# PyQt
from PyQt5.QtCore import QTranslator, QCoreApplication
# QGIS
from qgis.core import Qgis
# Graphium
from .graphium_qgis_connection_simple_dialog import GraphiumQGISConnectionSimpleDialog
from ..graphium_graph_management_api import GraphiumGraphManagementApi
from .model.graphium_server_type import GraphiumServerType
from ..settings import Settings


class GraphiumQGISConnectionManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, connection):
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
        # initialize settings
        self.settings = Settings()
        # initialize locale
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GraphiumQGIS_{}.qm'.format(self.settings.get_locale()))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GraphiumQGISConnectionSimpleDialog()

        self.connection = connection

        # for server_type in GraphiumServerType:
        #     self.dlg.cboServer.addItem(server_type.name, server_type.value)
        # self.dlg.cboServer.setCurrentText(self.connection.server.name)

        self.dlg.txtName.setText(self.connection.name)

        # self.dlg.txtHost.setText(self.connection.host)
        # self.dlg.txtPort.setText(str(self.connection.port) if self.connection.port is not None else '')
        # self.dlg.txtBaseUrl.setText(self.connection.base_url)
        self.dlg.txtSimpleUrl.setText(self.connection.get_simple_url())

        self.dlg.authConfigSelect.setConfigId(self.connection.auth_cfg)
        if self.settings.get_value('enable_auth', False):
            self.dlg.lblAuthLabel.setVisible(True)
            self.dlg.authConfigSelect.setVisible(True)
        else:
            self.dlg.lblAuthLabel.setVisible(False)
            self.dlg.authConfigSelect.setVisible(False)
        self.dlg.chkReadOnly.setChecked(self.connection.read_only)

        # self.dlg.tabWidgetConnection.currentChanged.connect(self.connection_widget_tab_changed)
        self.dlg.btnConnect.clicked.connect(self.connect_to_graphium)

        # graphium
        self.graphium = GraphiumGraphManagementApi()
        self.graph_names = []

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

    def connect_to_graphium(self):
        self.dlg.btnConnect.setEnabled(False)
        self.write_connection()
        if self.graphium.connect(self.connection):
            self.iface.messageBar().pushSuccess("Graphium", "Connecting to Graphium server [" +
                                                self.connection.name + "] succeeded")
        else:
            self.iface.messageBar().pushMessage("Graphium", "Connecting to Graphium server [" +
                                                self.connection.name + "] failed", level=Qgis.Warning)
        self.dlg.btnConnect.setEnabled(True)

    def connection_widget_tab_changed(self, index):
        self.write_connection(0 if index == 1 else 1)

    def write_connection(self, tab_index=-1):
        self.connection.name = self.dlg.txtName.text()
        # self.connection.server = GraphiumServerType[self.dlg.cboServer.currentText()]

        # tab_index = tab_index if tab_index >= 0 else self.dlg.tabWidgetConnection.currentIndex()
        # if tab_index == 0:
        url = self.dlg.txtSimpleUrl.text()
        if url[:7] == 'http://':
            protocol = 'http://'
            host_port_base_url = url[7:]
        elif url[:8] == 'https://':
            protocol = 'https://'
            host_port_base_url = url[8:]
        else:
            protocol = ''
            host_port_base_url = url

        if '/' in host_port_base_url:
            host_port, base_url = host_port_base_url.split('/', 1)
        else:
            host_port = host_port_base_url
            base_url = ''

        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, None

        self.connection.host = protocol + host
        self.connection.port = port if port else None
        self.connection.base_url = base_url

        self.connection.auth_cfg = self.dlg.authConfigSelect.configId()
        self.connection.read_only = self.dlg.chkReadOnly.isChecked()

        # else:
        #     self.connection.host = self.dlg.txtHost.text()
        #     try:
        #         if self.dlg.txtPort.text() != "":
        #             self.connection.port = int(self.dlg.txtPort.text())
        #         else:
        #             self.connection.port = None
        #     except ValueError:
        #         pass
        #     self.connection.base_url = self.dlg.txtBaseUrl.text()

        # self.dlg.txtHost.setText(self.connection.host)
        # self.dlg.txtPort.setText(str(self.connection.port) if self.connection.port else '')
        # self.dlg.txtBaseUrl.setText(self.connection.base_url)
        self.dlg.txtSimpleUrl.setText(self.connection.get_simple_url())

    def run(self):
        """Run method that performs all the real work"""

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.write_connection()
        return result
