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
# qgis imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingParameterString, QgsProcessingParameterEnum,
                       QgsProcessingAlgorithm, QgsProcessingParameterField, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink, QgsFeatureSink, QgsCoordinateReferenceSystem,
                       QgsProcessingMultiStepFeedback)
# plugin
from ...graphium_graph_data_api import (GraphiumGraphDataApi)
from ....graphium.connection.graphium_connection_manager import GraphiumConnectionManager
from ....graphium.settings import Settings


class UpdateSegmentAttributeAlgorithm(QgsProcessingAlgorithm):

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    INPUT = 'INPUT'
    SERVER_NAME = 'SERVER_NAME'
    GRAPH_NAME = 'GRAPH_NAME'
    GRAPH_VERSION = 'GRAPH_VERSION'
    FIELD_SEGMENT_ID = 'FIELD_SEGMENT_ID'
    SEGMENT_ATTRIBUTE = 'SEGMENT_ATTRIBUTE'
    TARGET_FIELD = 'TARGET_FIELD'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Data"
        self.alg_group_id = "graphdata"
        self.alg_name = self.tr("UpdateSegmentAttribute")
        self.alg_display_name = self.tr("Update Segment Attribute")

        self.connection_manager = GraphiumConnectionManager()
        self.connection_options = list()

        self.graph_name = ''
        self.graph_version = ''
        self.field_segment_id = ''
        self.field_start_to_end = ''
        self.segment_attribute = ''
        self.segment_attribute_label = ''
        self.target_field = ''

        # self.target_value_cache = {}

        self.segment_attribute_options = ['name', 'startNodeIndex', 'startNodeId', 'endNodeIndex', 'endNodeId',
                                          'maxSpeedTow', 'maxSpeedBkw', 'calcSpeedTow', 'calcSpeedBkw',
                                          'lanesTow', 'lanesBkw', 'frc', 'formOfWay', 'accessTow', 'accessBkw',
                                          'tunnel', 'bridge', 'urban', 'connection', 'geometry']

    def createInstance(self):
        return UpdateSegmentAttributeAlgorithm()

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
        return self.tr('This algorithm writes an attribute of a graph segment in a field of the vector data set.')

    def icon(self):
        return QIcon(os.path.join(self.plugin_path, 'icons/icon.svg'))

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def outputName(self):
        return self.tr('Segments with updated attribute')

    def initAlgorithm(self, config=None):
        """
        Definition of inputs and outputs of the algorithm, along with some other properties.
        """

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input layer'),
                                                              [QgsProcessing.TypeVector], None, False))

        self.addParameter(QgsProcessingParameterField(self.FIELD_SEGMENT_ID, self.tr('Segment ID field'),
                                                      'segment_id', 'INPUT'))
        self.addParameter(QgsProcessingParameterEnum(self.SEGMENT_ATTRIBUTE, self.tr('Segment attribute'),
                                                     self.segment_attribute_options, False, 0, False))
        self.addParameter(QgsProcessingParameterField(self.TARGET_FIELD, self.tr('Target field (will be updated)'),
                                                      'target', 'INPUT'))

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
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Output'),
                                                            QgsProcessing.TypeVector))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)

        source = self.parameterAsSource(parameters, self.INPUT, context)
        field_segment_id = self.parameterAsString(parameters, self.FIELD_SEGMENT_ID, context)
        segment_attribute_index = self.parameterAsInt(parameters, self.SEGMENT_ATTRIBUTE, context)
        segment_attribute = self.segment_attribute_options[segment_attribute_index]
        target_field = self.parameterAsString(parameters, self.TARGET_FIELD, context)

        server_name = self.connection_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)

        feedback.pushInfo("Connect to Graphium server '" + server_name + "' ...")

        graphium = GraphiumGraphDataApi(feedback)
        selected_connection = self.connection_manager.select_graphium_server(server_name)

        if selected_connection is None:
            feedback.reportError('Cannot select connection to Graphium', True)
            return {self.OUTPUT: None}

        if graphium.connect(selected_connection) is False:
            feedback.reportError('Cannot connect to [' + server_name + ']', True)
            return {self.OUTPUT: None}

        feedback.pushInfo("Start downloading task on Graphium server '" + server_name + "' ...")

        total = 100.0 / source.featureCount() if source.featureCount() else 0

        # Read segment IDs
        segment_ids = []
        attributes_per_segment = dict()
        for current, feature in enumerate(source.getFeatures()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            if not feature[field_segment_id]:
                continue

            if not feature[field_segment_id] in segment_ids:
                segment_ids.append(feature[field_segment_id])
            if len(segment_ids) > 50:
                self.get_segment_attributes(feedback, graphium, graph_name, graph_version, segment_attribute,
                                            segment_ids, attributes_per_segment)
            # Update the progress bar
            feedback.setProgress(int(current * total))
        if len(segment_ids) > 0:
            self.get_segment_attributes(feedback, graphium, graph_name, graph_version, segment_attribute,
                                        segment_ids, attributes_per_segment)

        feedback.setCurrentStep(1)
        feedback.pushInfo("Add attributes to features")

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, source.fields(),
                                               source.wkbType(), source.sourceCrs())

        for current, feature in enumerate(source.getFeatures()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            if feature[field_segment_id]:
                if int(feature[field_segment_id]) in attributes_per_segment:
                    feature[target_field] = attributes_per_segment[int(feature[field_segment_id])]
                else:
                    feedback.pushInfo("No attribute for segment " + str(feature[field_segment_id]))

            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        feedback.setProgress(100)

        return {
            self.OUTPUT: dest_id
        }

        # if 'waysegment' in response:
        #     if len(response['waysegment']) == 1:
        #         if self.segment_attribute in ['accessTow', 'accessBkw', 'connection']:
        #             feature[self.target_field] = json.dumps(response['waysegment'][0][self.segment_attribute])
        #         else:
        #             feature[self.target_field] = response['waysegment'][0][self.segment_attribute]

    def get_segment_attributes(self, feedback, graphium, graph_name, graph_version, attribute, segment_ids, attributes):

        response = graphium.get_segment(graph_name, graph_version, ",".join([str(s) for s in segment_ids]))
        if 'waysegment' in response:
            if len(response['waysegment']) >= 1:
                for segment in response['waysegment']:
                    attributes[segment['id']] = segment[attribute]
            else:
                feedback.reportError('No segment available', True)

        elif 'error' in response:
            if 'msg' in response['error']:
                feedback.reportError(response['error']['msg'], True)
        else:
            if 'graphVersionMetadata' in response:
                if response['graphVersionMetadata']['state'] == 'DELETED':
                    feedback.reportError('Graph version has been deleted', False)
                else:
                    feedback.reportError('Segment ' + str(segment_ids[0]) + ' not found', False)
            else:
                feedback.reportError('Unknown error', True)

        segment_ids.clear()
