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
# qgis imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterField, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString, QgsProcessingParameterFeatureSink, QgsProcessing, QgsGeometry,
                       QgsWkbTypes, QgsFeatureSink, QgsCoordinateReferenceSystem, QgsProcessingOutputNumber,
                       QgsProcessingMultiStepFeedback, QgsProcessingParameterEnum)
# plugin
from ....graphium.graphium_graph_data_api import GraphiumGraphDataApi
from ....graphium.connection.graphium_connection_manager import GraphiumConnectionManager
from ....graphium.settings import Settings


class AddSegmentGeometryAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm adds way segment geometries to a vector dataset without geometries associated
    with its features (attribute only table).
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    INPUT = 'INPUT'
    FIELD_SEGMENT_ID = 'FIELD_SEGMENT_ID'

    SERVER_NAME = 'SERVER_NAME'
    GRAPH_NAME = 'GRAPH_NAME'
    GRAPH_VERSION = 'GRAPH_VERSION'

    OUTPUT_SEGMENTS = 'OUTPUT_SEGMENTS'
    OUTPUT_SEGMENT_COUNT = 'OUTPUT_SEGMENT_COUNT'
    OUTPUT_SEGMENT_WITH_GEOMETRY_COUNT = 'OUTPUT_SEGMENT_WITH_GEOMETRY_COUNT'

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Data"
        self.alg_group_id = "graphdata"
        self.alg_name = "AddSegmentGeometry"
        self.alg_display_name = "Add Segment Geometry"

        self.connection_manager = GraphiumConnectionManager()
        self.connection_options = list()

    def createInstance(self):
        return AddSegmentGeometryAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm adds way segment geometries to a vector dataset without geometries associated '
                       'with its features (attribute only table). If no geometry could be found, no geometry will be '
                       'associated with the feature.')

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

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input layer'),
                                                              [QgsProcessing.TypeVector], None, False))
        self.addParameter(QgsProcessingParameterField(self.FIELD_SEGMENT_ID, self.tr('Segment ID field'), None,
                                                      self.INPUT, QgsProcessingParameterField.Any))

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

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_SEGMENTS, self.tr('Segments'),
                                                            QgsProcessing.TypeVectorLine))

        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_SEGMENT_COUNT, self.tr('Number of segments')))
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_SEGMENT_WITH_GEOMETRY_COUNT,
                                                 self.tr('Number of segments with geometry')))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        source = self.parameterAsSource(parameters, self.INPUT, context)
        field_segment_id = self.parameterAsString(parameters, self.FIELD_SEGMENT_ID, context)

        server_name = self.connection_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)

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

        feedback.setCurrentStep(2)
        feedback.pushInfo("Start downloading task on Graphium server '" + server_name + "' ...")

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_SEGMENTS, context, source.fields(),
                                               QgsWkbTypes.LineString, QgsCoordinateReferenceSystem('EPSG:4326'))

        segments_with_geometry = 0

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            response = graphium.get_segment(graph_name, graph_version, feature[field_segment_id])

            if 'waysegment' in response:
                if len(response['waysegment']) == 1:
                    new_geometry = QgsGeometry.fromWkt(response['waysegment'][0]['geometry'])
                    if new_geometry is not None:
                        feature.setGeometry(new_geometry)
                        segments_with_geometry += 1
                    else:
                        feedback.reportError('Cannot parse WKT geometry', True)
                else:
                    feedback.reportError('More than one segment', True)

            elif 'error' in response:
                if 'msg' in response['error']:
                    feedback.reportError(response['error']['msg'], True)
            else:
                if 'graphVersionMetadata' in response:
                    if response['graphVersionMetadata']['state'] == 'DELETED':
                        feedback.reportError('Graph version has been deleted', False)
                    else:
                        feedback.reportError('Segment ' + str(feature[field_segment_id]) + ' not found', False)
                else:
                    feedback.reportError('Unknown error', True)

            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        feedback.setProgress(100)

        return {
            self.OUTPUT_SEGMENTS: dest_id,
            self.OUTPUT_SEGMENT_COUNT: source.featureCount() if source.featureCount() else 0,
            self.OUTPUT_SEGMENT_WITH_GEOMETRY_COUNT: segments_with_geometry
        }
