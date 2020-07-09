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
from datetime import datetime
# PyQt5 imports
from PyQt5.QtGui import (QIcon)
# qgis imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterEnum, QgsProcessingParameterString,
                       QgsProcessingOutputString, QgsProcessingException)
# plugin
from ...graphium_graph_management_api import GraphiumGraphManagementApi
from ...connection.graphium_connection_manager import GraphiumConnectionManager
from ...settings import Settings


class UpdateGraphVersionValidityAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm updates the validity of a graph version.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    SERVER_NAME = 'SERVER_NAME'
    GRAPH_NAME = 'GRAPH_NAME'
    GRAPH_VERSION = 'GRAPH_VERSION'
    ATTRIBUTE = 'ATTRIBUTE'
    NEW_VALUE = 'NEW_VALUE'
    OUTPUT_NEW_VALUE = 'OUTPUT_NEW_VALUE'

    date_read_format = '%Y-%m-%d %H:%M:%S%z'

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Management"
        self.alg_group_id = "graphmanagement"
        self.alg_name = "UpdateGraphVersionValidity"
        self.alg_display_name = "Update Graph Version Validity"

        self.attribute_options = ['VALID_FROM', 'VALID_TO']

        self.connection_manager = GraphiumConnectionManager()
        self.connection_options = list()

    def createInstance(self):
        return UpdateGraphVersionValidityAlgorithm()

    def tags(self):
        return self.tr('update,validity,graph,version,graphium').split(',')

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm updates the validity of a graph version.')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon.svg'))

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

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

        self.addParameter(QgsProcessingParameterEnum(self.ATTRIBUTE, self.tr('Attribute'),
                                                     self.attribute_options, False, 0, False))

        self.addParameter(QgsProcessingParameterString(self.NEW_VALUE, self.tr('New value'), None, False, False))

        self.addOutput(QgsProcessingOutputString(self.OUTPUT_NEW_VALUE, self.tr('State')))

    def checkParameterValues(self, parameters, context):
        ok, message = super(UpdateGraphVersionValidityAlgorithm, self).checkParameterValues(parameters, context)
        if ok:
            new_value = self.parameterAsString(parameters, self.NEW_VALUE, context)
            if new_value != '':
                try:
                    datetime.strptime(new_value + '+0000', self.date_read_format)
                except ValueError:
                    try:
                        datetime.strptime(new_value, self.date_read_format)
                    except ValueError:
                        ok, message = False, 'Cannot parse new date (format ' + self.date_read_format + ')'

        return ok, message

    def processAlgorithm(self, parameters, context, feedback):

        feedback.setProgress(0)

        server_name = self.connection_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)
        attribute = self.attribute_options[self.parameterAsInt(parameters, self.ATTRIBUTE, context)]
        new_value = self.parameterAsString(parameters, self.NEW_VALUE, context)

        attribute_str = "validFrom" if attribute == 'VALID_FROM' else 'validTo'
        new_value_str = ""

        try:
            new_value_str = str(datetime.strptime(new_value + '+0000', self.date_read_format).timestamp() * 1000)
        except ValueError:
            try:
                new_value_str = str(datetime.strptime(new_value, self.date_read_format).timestamp() * 1000)
            except ValueError:
                raise QgsProcessingException("Cannot parse date (format should be " + self.date_read_format + ")")

        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumGraphManagementApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)

        if selected_connection is None:
            raise QgsProcessingException('Cannot select connection to Graphium')

        if graphium.connect(selected_connection) is False:
            raise QgsProcessingException('Cannot connect to Graphium')

        feedback.setProgress(10)
        feedback.pushInfo("Update validity of graph version '" + graph_version + "' ...")

        response = graphium.modify_graph_version_attribute(graph_name, graph_version, attribute_str, new_value_str)

        if attribute_str in response:
            return {self.OUTPUT_NEW_VALUE: response[attribute_str]}
        elif 'error' in response:
            if 'msg' in response['error']:
                if response['error']['msg'] == 'ContentNotFoundError':
                    raise QgsProcessingException('Graphium server "' + server_name + '" does not support updating' +
                                                 ' attributes!')
                elif response['error']['msg'] == 'UnprocessableEntity':
                    raise QgsProcessingException('The new attribute value is not valid!')
                else:
                    raise QgsProcessingException(response['error']['msg'])
        else:
            raise QgsProcessingException('Unknown error')
