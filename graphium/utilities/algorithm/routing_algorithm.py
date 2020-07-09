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
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import (QIcon)
# qgis imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingParameterEnum, QgsProcessingParameterString,
                       QgsProcessingParameterPoint, QgsProcessingParameterFeatureSink, QgsProcessing, QgsFeature,
                       QgsFeatureSink, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField, QgsGeometry,
                       QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback)
# plugin
from ...connection.model.graphium_server_type import GraphiumServerType
from ..graphium_utilities_api import GraphiumUtilitiesApi
from ....graphium.connection.graphium_connection_manager import GraphiumConnectionManager
from ....graphium.settings import Settings


class RoutingAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm finds the fastest or shortest route between two coordinates.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Utilities"
        self.alg_group_id = "graphutilities"
        self.alg_name = "routing"
        self.alg_display_name = "Routing"

        self.START_COORDINATE = 'START_COORDINATE'
        self.END_COORDINATE = 'END_COORDINATE'
        # self.CUT_SEGMENTS = 'CUT_SEGMENTS'
        self.ROUTING_MODE = 'ROUTING_MODE'
        self.ROUTING_CRITERIA = 'ROUTING_CRITERIA'
        self.SERVER_NAME = 'SERVER_NAME'
        self.GRAPH_NAME = 'OVERRIDE_GRAPH_NAME'
        self.GRAPH_VERSION = 'OVERRIDE_GRAPH_VERSION'
        self.OUTPUT = 'OUTPUT'
        self.OUTPUT_PATH = 'OUTPUT_PATH'

        self.connection_manager = GraphiumConnectionManager()
        self.server_name_options = list()
        self.routing_mode_options = ['CAR', 'BIKE', 'PEDESTRIAN', 'PEDESTRIAN_BARRIERFREE']
        self.routing_criteria_options = ['LENGTH', 'MIN_DURATION', 'CURRENT_DURATION']

    def createInstance(self):
        return RoutingAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('Use this algorithm to find the fastest or shortest route between two coordinates. The route '
                       'can be optimized for different modes of transport.\n\n'
                       'The start and end coordinates can be set (1) with the [...] button right to the text input or '
                       '(2) manually according to format "lon,lat [coordinate reference system]" '
                       '(e.g. 13.0,47.8 [EPSG:4326])')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon_routing.svg'))

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def initAlgorithm(self, config=None):
        """
        Definition of inputs and outputs of the algorithm, along with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        # self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input gpx file'),
        #                                                       [QgsProcessing.TypeVectorLine]))

        self.addParameter(QgsProcessingParameterPoint(self.START_COORDINATE,
                                                      self.tr('Start coordinate'),
                                                      None, False))
        self.addParameter(QgsProcessingParameterPoint(self.END_COORDINATE,
                                                      self.tr('End coordinate'),
                                                      None, False))
        self.addParameter(QgsProcessingParameterEnum(self.ROUTING_MODE,
                                                     self.tr('Select routing mode'),
                                                     options=self.routing_mode_options,
                                                     allowMultiple=False, defaultValue=0, optional=False))
        self.addParameter(QgsProcessingParameterEnum(self.ROUTING_CRITERIA,
                                                     self.tr('Select routing criteria'),
                                                     options=self.routing_criteria_options,
                                                     allowMultiple=False, defaultValue=1, optional=False))
        # self.addParameter(QgsProcessingParameterBoolean(self.CUT_SEGMENTS,
        #                                                 self.tr('Cut segments'),
        #                                                 True, True))

        # read server connections and prepare enum items
        self.server_name_options.clear()
        selected_graph_server = Settings.get_selected_graph_server()
        selected_index = 0
        for index, connection in enumerate(self.connection_manager.read_connections()):
            self.server_name_options.append(connection.name)
            if selected_index == 0 and isinstance(selected_graph_server, str)\
                    and connection.name == selected_graph_server:
                selected_index = index
        self.addParameter(QgsProcessingParameterEnum(self.SERVER_NAME, self.tr('Server name'),
                                                     self.server_name_options, False, selected_index, False))

        s = Settings.get_selected_graph_name()
        default_graph_name = ''
        if isinstance(s, str):
            default_graph_name = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_NAME, self.tr('Graph name'),
                                                       default_graph_name, False, True))
        s = Settings.get_selected_graph_version()
        default_graph_version = ''
        if isinstance(s, str):
            default_graph_version = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_VERSION, self.tr('Graph version'),
                                                       default_graph_version, False, True))

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Routing output'),
                                                            QgsProcessing.TypeVectorLine))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_PATH, self.tr('Routing path output'),
                                                            QgsProcessing.TypeVector))

    def processAlgorithm(self, parameters, context, model_feedback):

        # source: 'export as python script' in processing modeler
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)

        start_coordinate = self.parameterAsPoint(parameters, self.START_COORDINATE, context,
                                                 QgsCoordinateReferenceSystem(4326))
        end_coordinate = self.parameterAsPoint(parameters, self.END_COORDINATE, context,
                                               QgsCoordinateReferenceSystem(4326))
        routing_mode = self.routing_mode_options[self.parameterAsInt(parameters, self.ROUTING_MODE, context)]
        routing_criteria = self.routing_criteria_options[self.parameterAsInt(parameters, self.ROUTING_CRITERIA,
                                                                             context)]
        # cut_segments = self.parameterAsBool(parameters, self.CUT_SEGMENTS, context)

        server_name = self.server_name_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)

        # Connect to Graphium
        feedback.setCurrentStep(2)
        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumUtilitiesApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)
        if selected_connection is None:
            feedback.reportError('Cannot select connection to Graphium', True)
            return {self.OUTPUT: None, self.OUTPUT_PATH: None}

        if graphium.connect(selected_connection) is False:
            feedback.reportError('Cannot connect to Graphium', True)
            return {self.OUTPUT: None, self.OUTPUT_PATH: None}

        feedback.pushInfo("Start Routing task on Graphium server '" + server_name + "' ...")
        response = graphium.do_routing(graph_name, graph_version, start_coordinate.x(), start_coordinate.y(),
                                       end_coordinate.x(), end_coordinate.y(), datetime.today(), None,
                                       routing_mode, routing_criteria)

        # Process routing result
        if 'route' in response:
            if response['route']['length'] == 0:
                feedback.reportError('No route found', False)
                return {self.OUTPUT: None, self.OUTPUT_PATH: None}
        elif 'error' in response:
            if 'msg' in response['error']:
                if response['error']['msg'] == 'ContentNotFoundError':
                    feedback.reportError('Graphium server "' + server_name + '" does not support routing',
                                         True)
                else:
                    feedback.reportError(response['error']['msg'], True)
            return {self.OUTPUT: None, self.OUTPUT_PATH: None}
        else:
            feedback.reportError('Unknown routing error', True)
            feedback.reportError(str(response), True)
            return {self.OUTPUT: None, self.OUTPUT_PATH: None}

        # create feature output
        feedback.setCurrentStep(3)
        vector_layer = self.prepare_vector_layer('route')

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, vector_layer.fields(),
                                               QgsWkbTypes.LineString, vector_layer.sourceCrs())
        if response['route']['geometry'] is not None:
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(response['route']['geometry']))
            feature.setFields(vector_layer.fields(), True)
            for attribute_key in response['route']:
                if feedback.isCanceled():
                    break
                try:
                    feature.setAttribute(attribute_key, response['route'][attribute_key])
                except KeyError:
                    pass
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        # create path output
        feedback.setCurrentStep(4)

        path_layer = self.prepare_path_layer('route_path')

        (sink_path, dest_id_path) = self.parameterAsSink(parameters, self.OUTPUT_PATH, context, path_layer.fields(),
                                                         QgsWkbTypes.NoGeometry, vector_layer.sourceCrs())
        if response['route']['geometry'] is not None:
            total = 100.0 / len(response['route']['segments'])
            for current, path_segment in enumerate(response['route']['segments']):
                if feedback.isCanceled():
                    break
                feature = QgsFeature()
                feature.setFields(path_layer.fields(), True)
                feature.setAttribute('order', current)
                feature.setAttribute('segment_id', path_segment['id'])
                feature.setAttribute('linkDirectionForward', path_segment['linkDirectionForward'])
                sink_path.addFeature(feature, QgsFeatureSink.FastInsert)
                feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id, self.OUTPUT_PATH: dest_id_path}

    @staticmethod
    def prepare_vector_layer(layer_name):
        layer_definition = 'LineString?crs=epsg:4326'
        vector_layer = QgsVectorLayer(layer_definition, layer_name, "memory")

        # Enter editing mode
        vector_layer.startEditing()
        attributes = list()
        attributes.append(QgsField('length', QVariant.Double, 'Real'))
        attributes.append(QgsField('duration', QVariant.Int, 'Integer'))
        attributes.append(QgsField('runtimeInMs', QVariant.Int, 'Integer'))
        attributes.append(QgsField('graphName', QVariant.String, 'String'))
        attributes.append(QgsField('graphVersion', QVariant.String, 'String'))
        vector_layer.dataProvider().addAttributes(attributes)
        vector_layer.updateFields()

        return vector_layer

    @staticmethod
    def prepare_path_layer(layer_name):
        path_layer = QgsVectorLayer('None', layer_name, "memory")
        # Enter editing mode
        path_layer.startEditing()
        attributes = list()
        attributes.append(QgsField('order', QVariant.Int, 'Integer'))
        attributes.append(QgsField('segment_id', QVariant.Int, 'Integer'))
        attributes.append(QgsField('linkDirectionForward', QVariant.String, 'String'))
        path_layer.dataProvider().addAttributes(attributes)
        path_layer.updateFields()

        return path_layer
