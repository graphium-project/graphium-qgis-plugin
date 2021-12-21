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
import json
# PyQt5 imports
from PyQt5.QtCore import (QVariant)
from PyQt5.QtGui import (QIcon)
# qgis imports
from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingParameterFile, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsProcessingParameterString, QgsProcessingParameterFeatureSink, QgsProcessing,
                       QgsFeatureSink, QgsWkbTypes, QgsProcessingException, QgsProcessingOutputNumber,
                       QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterEnum)
# plugin
from ...connection.model.graphium_server_type import GraphiumServerType
from ..graphium_utilities_api import GraphiumUtilitiesApi
from ...connection.graphium_connection_manager import GraphiumConnectionManager
from ...settings import Settings


class MapMatcherAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to link trajectories to the road network.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Utilities"
        self.alg_group_id = "graphutilities"
        self.alg_name = "mapmatcher"
        self.alg_display_name = "Map Matcher"

        self.INPUT = 'INPUT'
        self.SERVER_NAME = 'SERVER_NAME'
        self.GRAPH_NAME = 'GRAPH_NAME'
        self.GRAPH_VERSION = 'GRAPH_VERSION'
        self.ROUTING_MODE = 'ROUTING_MODE'
        self.OUTPUT_MATCHED_SEGMENTS = 'OUTPUT_MATCHED_SEGMENTS'
        self.OUTPUT_NR_OF_U_TURNS = 'OUTPUT_NR_OF_U_TURNS'
        self.OUTPUT_NR_OF_SHORTEST_PATH_SEARCHES = 'OUTPUT_NR_OF_SHORTEST_PATH_SEARCHES'
        self.OUTPUT_LENGTH = 'OUTPUT_LENGTH'
        self.OUTPUT_MATCHED_FACTOR = 'OUTPUT_MATCHED_FACTOR'
        self.OUTPUT_MATCHED_POINTS = 'OUTPUT_MATCHED_POINTS'
        self.OUTPUT_CERTAIN_PATH_END_SEGMENT_ID = 'OUTPUT_CERTAIN_PATH_END_SEGMENT_ID'

        self.connection_manager = GraphiumConnectionManager()
        self.server_name_options = list()
        self.graph_version_options = ['VALID_AT_TIME_OF_TRAJECTORY', 'CURRENTLY_VALID']

        self.routing_mode_options = ['car', 'bike']

    def createInstance(self):
        return MapMatcherAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to link trajectories to the road network.')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon_map_matcher.svg'))

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
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input track file'),
                                                     QgsProcessingParameterFile.Behavior.File, 'json',
                                                     None, False))  # , "*.gpx;*.json"))  # does not work in QGIS 3.22

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
        graph_name = ''
        if isinstance(s, str):
            graph_name = s

        self.addParameter(QgsProcessingParameterString(self.GRAPH_NAME, self.tr('Graph name'), graph_name,
                                                       False, False))

        self.addParameter(QgsProcessingParameterEnum(self.GRAPH_VERSION, self.tr('Graph version'),
                                                     self.graph_version_options, False, 0, False))

        self.addParameter(QgsProcessingParameterEnum(self.ROUTING_MODE,
                                                     self.tr('Select routing mode'),
                                                     options=self.routing_mode_options,
                                                     allowMultiple=False, defaultValue=0, optional=False))

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_MATCHED_SEGMENTS,
                                                            self.tr('Map matching output'),
                                                            QgsProcessing.TypeVectorLine))

        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_NR_OF_U_TURNS, self.tr('Number of U-Turns')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_NR_OF_SHORTEST_PATH_SEARCHES,
                                                 self.tr('Number of shortest path searches')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_LENGTH, self.tr('Map-matched length')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_MATCHED_FACTOR, self.tr('Matched factor')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_MATCHED_POINTS, self.tr('Number of matched track points')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_CERTAIN_PATH_END_SEGMENT_ID,
                                                 self.tr('ID of last certain path segment')))

    def processAlgorithm(self, parameters, context, model_feedback):

        # source: 'export as python script' in processing modeler
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)

        # pass
        source = self.parameterAsFile(parameters, self.INPUT, context)
        server_name = self.server_name_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.graph_version_options[self.parameterAsInt(parameters, self.GRAPH_VERSION, context)]
        routing_mode = self.routing_mode_options[self.parameterAsInt(parameters, self.ROUTING_MODE, context)]

        if os.path.splitext(source)[-1].lower() == '.json':
            feedback.pushInfo('Load json track file')
            with open(source) as json_data:
                track_data = json.load(json_data)
        elif os.path.splitext(source)[-1].lower() == '.gpx':
            feedback.pushInfo('Convert track file from GPX to JSON format using Graphium:Gpx2JsonConverter')
            try:
                output = processing.run("Graphium:gpx2jsonconverter", parameters={
                    'INPUT': source,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }, is_child_algorithm=True, context=context, feedback=feedback)['OUTPUT']
                with open(output) as json_data:
                    track_data = json.load(json_data)
            except QgsProcessingException as e:
                feedback.reportError("Could not convert GPX file to JSON: " + str(e), True)
                return {self.OUTPUT_MATCHED_SEGMENTS: None}
        else:
            feedback.reportError("Wrong track file format (" + os.path.splitext(source)[-1].lower() + ")", True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}

        # Connect to Graphium
        feedback.setCurrentStep(2)
        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumUtilitiesApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)
        if selected_connection is None:
            feedback.reportError('Cannot select connection to Graphium', True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}

        if graphium.connect(selected_connection) is False:
            feedback.reportError('Cannot connect to Graphium', True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}

        feedback.pushInfo("Start Map-Matching task on Graphium server '" + server_name + "' ...")
        response = graphium.do_map_matching(track_data, graph_name, graph_version, routing_mode)

        # Process map matching result
        if 'segments' in response:
            feedback.pushInfo('Finished map matching task!')
        elif 'error' in response:
            if 'msg' in response['error']:
                if response['error']['msg'] == 'ContentNotFoundError':
                    feedback.reportError('Graphium server "' + server_name + '" does not support map matching',
                                         True)
                else:
                    feedback.reportError(response['error']['msg'], True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}
        elif 'exception' in response:
            feedback.reportError(response['exception'], True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}
        else:
            feedback.reportError('Unknown mapmatching error', True)
            return {self.OUTPUT_MATCHED_SEGMENTS: None}

        feedback.setCurrentStep(3)
        feedback.pushInfo("Prepare result vector layer ...")
        vector_layer = self.prepare_vector_layer('matched_track')

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_MATCHED_SEGMENTS, context, vector_layer.fields(),
                                               QgsWkbTypes.LineString, vector_layer.sourceCrs())

        total = 100.0 / len(response['segments'])
        for current, segment in enumerate(response['segments']):
            if feedback.isCanceled():
                break
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(segment['geometry']))
            feature.setFields(vector_layer.fields(), True)
            feature.setAttribute('order', current)
            for attribute_key in segment:
                try:
                    feature.setAttribute(attribute_key, segment[attribute_key])
                except KeyError:
                    pass
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        feedback.pushInfo("Finished preparing vector layer " + dest_id)
        return {self.OUTPUT_MATCHED_SEGMENTS: dest_id,
                self.OUTPUT_NR_OF_U_TURNS: response['nrOfUTurns'],
                self.OUTPUT_NR_OF_SHORTEST_PATH_SEARCHES: response['nrOfShortestPathSearches'],
                self.OUTPUT_LENGTH: response['length'],
                self.OUTPUT_MATCHED_FACTOR: response['matchedFactor'],
                self.OUTPUT_MATCHED_POINTS: response['matchedPoints'],
                self.OUTPUT_CERTAIN_PATH_END_SEGMENT_ID: response['certainPathEndSegmentId']
                }

    @staticmethod
    def prepare_vector_layer(layer_name):
        layer_definition = 'LineString?crs=epsg:4326'
        vector_layer = QgsVectorLayer(layer_definition, layer_name, "memory")
        data_provider = vector_layer.dataProvider()

        # Enter editing mode
        vector_layer.startEditing()
        attributes = list()
        attributes.append(QgsField('order', QVariant.Int, 'Integer'))
        attributes.append(QgsField('segmentId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('startPointIndex', QVariant.Int, 'Integer'))
        attributes.append(QgsField('endPointIndex', QVariant.Int, 'Integer'))
        attributes.append(QgsField('enteringThroughStartNode', QVariant.Bool, 'String'))
        attributes.append(QgsField('leavingThroughStartNode', QVariant.Bool, 'String'))
        attributes.append(QgsField('enteringThroughEndNode', QVariant.Bool, 'String'))
        attributes.append(QgsField('leavingThroughEndNode', QVariant.Bool, 'String'))
        attributes.append(QgsField('startSegment', QVariant.Bool, 'String'))
        attributes.append(QgsField('afterSkippedPart', QVariant.Bool, 'String'))
        attributes.append(QgsField('fromPathSearch', QVariant.Bool, 'String'))
        attributes.append(QgsField('uTurnSegment', QVariant.Bool, 'String'))
        attributes.append(QgsField('weight', QVariant.Double, 'Real'))
        attributes.append(QgsField('matchedFactor', QVariant.Double, 'Real'))
        data_provider.addAttributes(attributes)
        vector_layer.updateFields()

        return vector_layer
