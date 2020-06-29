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

import os
# PyQt5 imports
from PyQt5.QtGui import (QIcon)
# from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingParameterEnum, QgsProcessingParameterString, QgsProcessingOutputString)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
# plugin
from ...graphium_graph_management_api import GraphiumGraphManagementApi
from ...connection.graphium_connection_manager import GraphiumConnectionManager
from ...settings import Settings


class ActivateGraphVersionAlgorithm(QgisAlgorithm):
    """
    This algorithm activates a graph version.
    """

    plugin_path = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

    SERVER_NAME = 'SERVER_NAME'
    GRAPH_NAME = 'GRAPH_NAME'
    GRAPH_VERSION = 'GRAPH_VERSION'
    OUTPUT_STATE = 'OUTPUT_STATE'

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Management"
        self.alg_group_id = "graphmanagement"
        self.alg_name = "ActivateGraphVersion"
        self.alg_display_name = "Activate Graph Version"

        self.connection_manager = GraphiumConnectionManager()
        self.connection_options = list()

    def tags(self):
        return self.tr('activate,graph,version,graphium').split(',')

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm activates a graph version. The state will be changed to \'ACTIVE\'.\n\nOnly '
                       'activated graph versions are applied in  utilities like routing or mapmatching.')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon.svg'))

    def initAlgorithm(self, config=None):
        """
        Definition of inputs and outputs of the algorithm, along with some other properties.
        """

        # read server connections and prepare enum items
        self.connection_options.clear()
        selected_graph_server = Settings.get_selected_graph_server()
        selected_index = 0
        for index, connection in enumerate(self.connection_manager.read_connections()):
            self.connection_options.append(connection.name)
            if selected_index == 0 and isinstance(selected_graph_server, str)\
                    and connection.name == selected_graph_server:
                selected_index = index
        self.addParameter(QgsProcessingParameterEnum(self.SERVER_NAME, self.tr('Server name'),
                                                     self.connection_options, False, selected_index, False))

        s = Settings.get_selected_graph_name()
        graph_name = ''
        if isinstance(s, str):
            graph_name = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_NAME, self.tr('Graph name'), graph_name,
                                                       False, False))

        s = Settings.get_selected_graph_version()
        graph_version = ''
        if isinstance(s, str):
            graph_version = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_VERSION, self.tr('Graph version'), graph_version,
                                                       False, False))

        self.addOutput(QgsProcessingOutputString(self.OUTPUT_STATE, self.tr('State')))

    def processAlgorithm(self, parameters, context, feedback):

        feedback.setProgress(0)

        server_name = self.connection_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)

        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumGraphManagementApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)

        if selected_connection is None:
            feedback.reportError('Cannot select connection to Graphium', True)
            return False

        if graphium.connect(selected_connection) is False:
            feedback.reportError('Cannot connect to Graphium', True)
            return False

        feedback.setProgress(10)
        feedback.pushInfo("Activate graph version '" + graph_version + "' ...")

        response = graphium.modify_graph_version_attribute(graph_name, graph_version, 'state', 'ACTIVE')

        if 'state' in response:
            return {self.OUTPUT_STATE: response['state']}
        elif 'error' in response:
            if 'msg' in response['error']:
                feedback.reportError(response['error']['msg'], True)
            return {self.OUTPUT_STATE: None}
        else:
            feedback.reportError('Unknown error', True)
            return {self.OUTPUT_STATE: None}
