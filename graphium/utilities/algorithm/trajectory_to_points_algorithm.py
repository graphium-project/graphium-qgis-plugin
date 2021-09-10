# -*- coding: utf-8 -*-

"""
/***************************************************************************
 QGIS plugin 'Graphium'
/***************************************************************************
 *
 * Copyright 2021 Simon Gröchenig @ Salzburg Research
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
import datetime
# PyQt imports
from qgis.PyQt.QtCore import (QCoreApplication, QDateTime, QDate, QTime, QTimeZone, QVariant)
from qgis.PyQt.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterFeatureSink, QgsProcessingAlgorithm,
                       QgsProcessingOutputNumber, QgsProcessing, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsWkbTypes, QgsFeatureSink, QgsPoint, QgsCoordinateReferenceSystem, QgsFields)


class TrajectoryToPointsAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to convert a Graphium trajectory (JSON) to a point layer.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Utilities"
        self.alg_group_id = "graphutilities"
        self.alg_name = "trajectoryToPoints"
        self.alg_display_name = "Trajectory to Points Converter"

        self.INPUT = 'INPUT'
        self.OUTPUT_POINT_LAYER = 'OUTPUT'
        self.NUMBER_TRACK_POINTS = 'NUMBER_TRACK_POINTS'

    def createInstance(self):
        return TrajectoryToPointsAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to convert a Graphium trajectory (JSON) to a point layer.')

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

        self.addParameter(QgsProcessingParameterFile(self.INPUT, self.tr('Input track file'),
                                                     0, 'json', None, False))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_POINT_LAYER, self.tr('Track point layer'),
                                                            QgsProcessing.TypeVectorPoint))

        self.addOutput(QgsProcessingOutputNumber(self.NUMBER_TRACK_POINTS, self.tr('Number of track points')))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsFile(parameters, self.INPUT, context)

        with open(source) as json_data:
            json_track = json.load(json_data)

        if 'trackPoints' not in json_track:
            return {
                self.OUTPUT_MATCHED_SEGMENTS: None,
                self.NUMBER_TRACK_POINTS: 0
            }

        vector_layer_fields = QgsFields()
        vector_layer_fields.append(QgsField('id', QVariant.Int, 'Integer'))
        vector_layer_fields.append(QgsField('timestamp', QVariant.DateTime, 'String'))
        vector_layer_fields.append(QgsField('h', QVariant.Double, 'Double'))
        vector_layer_fields.append(QgsField('distCalc', QVariant.Double, 'Double'))
        vector_layer_fields.append(QgsField('vCalc', QVariant.Double, 'Double'))
        vector_layer_fields.append(QgsField('durationCalc', QVariant.Double, 'Double'))
        vector_layer_fields.append(QgsField('aCalc', QVariant.Double, 'Double'))
        vector_layer_fields.append(QgsField('tags', QVariant.Map, 'JSON'))
        vector_layer_crs = QgsCoordinateReferenceSystem('EPSG:4326')

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_POINT_LAYER, context, vector_layer_fields,
                                               QgsWkbTypes.Point, vector_layer_crs)

        total = 100.0 / len(json_track['trackPoints'])
        for current, track_point in enumerate(json_track['trackPoints']):
            if feedback.isCanceled():
                break
            feature = QgsFeature()
            if 'z' in track_point:
                feature.setGeometry(QgsPoint(track_point['x'], track_point['y'], track_point['z']))
            else:
                feature.setGeometry(QgsPoint(track_point['x'], track_point['y']))
            feature.setFields(vector_layer_fields, True)
            timestamp_sec = track_point['t']
            timestamp = datetime.datetime.fromtimestamp(timestamp_sec / 1000)
            feature.setAttribute('timestamp', str(timestamp))
            feedback.pushInfo(str(track_point['id']))
            for attribute in track_point:
                if attribute != 'x' and attribute != 'y' and attribute != 'z' and attribute != 't':
                    if track_point[attribute]:
                        feature.setAttribute(attribute, str(track_point[attribute]))

            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        feedback.pushInfo("Finished preparing vector layer " + dest_id)

        return {
            self.OUTPUT_POINT_LAYER: dest_id,
            self.NUMBER_TRACK_POINTS: len(json_track['trackPoints'])
        }
