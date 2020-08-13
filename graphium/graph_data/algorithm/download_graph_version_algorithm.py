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
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (QVariant)
# qgis imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsVectorLayer, QgsProcessingAlgorithm, QgsProcessingParameterString, QgsField, QgsGeometry,
                       QgsProcessingMultiStepFeedback, QgsFeature, QgsFeatureSink, QgsWkbTypes, QgsProcessing,
                       QgsProcessingParameterEnum, QgsProcessingParameterFeatureSink, QgsProcessingOutputNumber,
                       QgsProcessingParameterBoolean, QgsProcessingParameterFileDestination)
# plugin
from ....graphium.graphium_graph_data_api import GraphiumGraphDataApi
from ....graphium.connection.graphium_connection_manager import GraphiumConnectionManager
from ....graphium.settings import Settings


class DownloadGraphVersionAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithms downloads all segments of a graph version dataset.
    """

    SERVER_NAME = 'SERVER_NAME'
    GRAPH_NAME = 'GRAPH_NAME'
    GRAPH_VERSION = 'GRAPH_VERSION'
    HD_WAYSEGMENTS = 'HD_WAYSEGMENTS'

    SAVE_JSON_FILE = 'SAVE_JSON_FILE'
    OUTPUT_SEGMENT_COUNT = 'OUTPUT_SEGMENT_COUNT'
    OUTPUT_SEGMENTS = 'OUTPUT_SEGMENTS'
    OUTPUT_JSON = 'OUTPUT_JSON'

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        self.alg_group = "Graph Data"
        self.alg_group_id = "graphdata"
        self.alg_name = "DownloadGraphVersion"
        self.alg_display_name = "Download Graph Version"

        self.connection_manager = GraphiumConnectionManager()
        self.connection_options = list()
        self.settings = Settings()

    def createInstance(self):
        return DownloadGraphVersionAlgorithm()

    def tags(self):
        return self.tr('add,vertex,vertices,points,nodes').split(',')

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithms downloads all segments of a graph version dataset. A new layer containing all '
                       'way segments is added to the map.')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon.svg'))

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def outputName(self):
        return self.tr('Download Graph Version')

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

        if self.settings.is_hd_enabled():
            self.addParameter(QgsProcessingParameterBoolean(self.HD_WAYSEGMENTS, self.tr('HD Waysegments'),
                                                            False, True))

        self.addParameter(QgsProcessingParameterBoolean(self.SAVE_JSON_FILE, self.tr('Save JSON file'),
                                                        'False', True))

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_SEGMENTS, self.tr('Segments'),
                                                            QgsProcessing.TypeVectorLine))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_JSON, self.tr('JSON graph file'),
                                                                'JSON files (*.json)', optional=True))

        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_SEGMENT_COUNT, self.tr('Number of segments')))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)

        server_name = self.connection_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)
        if self.settings.is_hd_enabled():
            is_hd_segments = self.parameterAsBool(parameters, self.HD_WAYSEGMENTS, context)
        else:
            is_hd_segments = False
        save_json_file = self.parameterAsBoolean(parameters, self.SAVE_JSON_FILE, context)
        json_file = self.parameterAsFileOutput(parameters, self.OUTPUT_JSON, context)

        # Connect to Graphium
        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumGraphDataApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)

        if selected_connection is None:
            feedback.reportError('Cannot select connection to Graphium', True)
            return {self.OUTPUT_SEGMENTS: None}

        if graphium.connect(selected_connection) is False:
            feedback.reportError('Cannot connect to Graphium', True)
            return {self.OUTPUT_SEGMENTS: None}

        feedback.pushInfo("Start downloading task on Graphium server '" + server_name + "' ...")
        response = graphium.export_graph(graph_name, graph_version, is_hd_segments)

        if save_json_file:
            feedback.pushInfo("Write graph to JSON file...")
            with open(json_file, 'w') as output_file:
                output_file.write(json.dumps(response))

        feedback.setCurrentStep(2)
        if 'graphVersionMetadata' in response:
            if response['graphVersionMetadata']['segmentsCount'] == 0:
                feedback.reportError('No segments available', False)
                return {self.OUTPUT_SEGMENT_COUNT: 0}
            elif response['graphVersionMetadata']['state'] == 'DELETED':
                feedback.reportError('Graph version has been deleted', False)
                return {self.OUTPUT_SEGMENT_COUNT: 0}
        elif 'error' in response:
            if 'msg' in response['error']:
                feedback.reportError(response['error']['msg'], True)
            return {self.OUTPUT_SEGMENT_COUNT: 0}
        else:
            feedback.reportError('Unknown error', True)
            return {self.OUTPUT_SEGMENT_COUNT: 0}

        feedback.pushInfo("Prepare result vector layer ...")
        vector_layer = self.prepare_vector_layer('segments_' + graph_name + '_' + graph_version,
                                                 response['graphVersionMetadata']['type'])

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_SEGMENTS, context, vector_layer.fields(),
                                               QgsWkbTypes.LineString, vector_layer.sourceCrs())

        total = 100.0 / len(response[response['graphVersionMetadata']['type']])
        for current, segment in enumerate(response[response['graphVersionMetadata']['type']]):
            if feedback.isCanceled():
                break
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(segment['geometry']))
            feature.setFields(vector_layer.fields(), True)
            for attribute_key in segment:
                try:
                    if attribute_key == 'accessTow' or attribute_key == 'accessBkw' or attribute_key == 'tags':
                        feature.setAttribute(attribute_key, json.dumps(segment[attribute_key]))
                    else:
                        feature.setAttribute(attribute_key, segment[attribute_key])
                except KeyError:
                    pass
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        feedback.pushInfo("Finished preparing vector layer " + dest_id)
        return {self.OUTPUT_SEGMENTS: dest_id,
                self.OUTPUT_JSON: json_file if save_json_file else None,
                self.OUTPUT_SEGMENT_COUNT: response['graphVersionMetadata']['segmentsCount']
                }

    @staticmethod
    def prepare_vector_layer(layer_name, layer_type):
        layer_definition = 'LineString?crs=epsg:4326'
        vector_layer = QgsVectorLayer(layer_definition, layer_name, "memory")
        data_provider = vector_layer.dataProvider()

        # Enter editing mode
        vector_layer.startEditing()
        attributes = list()
        attributes.append(QgsField('id', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('name', QVariant.String, 'Integer'))
        attributes.append(QgsField('startNodeIndex', QVariant.Int, 'Integer'))
        attributes.append(QgsField('startNodeId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('endNodeIndex', QVariant.Int, 'Integer'))
        attributes.append(QgsField('endNodeId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('maxSpeedTow', QVariant.Int, 'Integer'))
        attributes.append(QgsField('maxSpeedBkw', QVariant.Int, 'Integer'))
        attributes.append(QgsField('calcSpeedTow', QVariant.Int, 'Integer'))
        attributes.append(QgsField('calcSpeedBkw', QVariant.Int, 'Integer'))
        attributes.append(QgsField('lanesTow', QVariant.Int, 'Integer'))
        attributes.append(QgsField('lanesBkw', QVariant.Int, 'Integer'))
        attributes.append(QgsField('frc', QVariant.Int, 'Integer'))
        attributes.append(QgsField('formOfWay', QVariant.String, 'String'))
        attributes.append(QgsField('accessTow', QVariant.String, 'String'))
        attributes.append(QgsField('accessBkw', QVariant.String, 'String'))
        attributes.append(QgsField('tunnel', QVariant.Bool, 'Boolean'))
        attributes.append(QgsField('bridge', QVariant.Bool, 'Boolean'))
        attributes.append(QgsField('urban', QVariant.Bool, 'Boolean'))
        attributes.append(QgsField('length', QVariant.Double, 'Double'))
        attributes.append(QgsField('tags', QVariant.String, 'String'))
        attributes.append(QgsField('leftBorderGeometry', QVariant.String, 'String'))
        attributes.append(QgsField('leftBorderStartNodeId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('leftBorderEndNodeId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('rightBorderGeometry', QVariant.String, 'String'))
        attributes.append(QgsField('rightBorderStartNodeId', QVariant.LongLong, 'Integer'))
        attributes.append(QgsField('rightBorderEndNodeId', QVariant.LongLong, 'Integer'))
        data_provider.addAttributes(attributes)
        vector_layer.updateFields()

        return vector_layer
