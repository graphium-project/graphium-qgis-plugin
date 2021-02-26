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
# PyQt imports
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QDate, QTime, QTimeZone
from qgis.PyQt.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingParameterFeatureSource, QgsProcessingParameterFileDestination,
                       QgsProcessingAlgorithm, QgsProcessingOutputNumber, QgsProcessing, QgsProcessingParameterField,
                       QgsProcessingParameterNumber)


class PointsToTrajectoryAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to convert a layer with points to a Graphium trajectory (JSON).
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Utilities"
        self.alg_group_id = "graphutilities"
        self.alg_name = "pointsToTrajectory"
        self.alg_display_name = "Points to Trajectory Converter"

        self.INPUT = 'INPUT'
        self.TRACK_ID = 'TRACK_ID'
        self.TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
        self.OUTPUT = 'OUTPUT'
        self.NUMBER_TRACK_POINTS = 'NUMBER_TRACK_POINTS'

    def createInstance(self):
        return PointsToTrajectoryAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to convert a point layer to a Graphium trajectory (JSON).')

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

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input point layer'),
                                                              [QgsProcessing.TypeVectorPoint], None, False))

        self.addParameter(QgsProcessingParameterField(self.TIMESTAMP_FIELD, self.tr('Timestamp field'),
                                                      parentLayerParameterName=self.INPUT,
                                                      type=QgsProcessingParameterField.DateTime))

        self.addParameter(QgsProcessingParameterNumber(self.TRACK_ID, self.tr('Track ID'),
                                                       QgsProcessingParameterNumber.Integer, 0, False))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT, self.tr('JSON trajectory file'),
                                                                'JSON files (*.json)', optional=True))

        self.addOutput(QgsProcessingOutputNumber(self.NUMBER_TRACK_POINTS, self.tr('Number of track points')))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        timestamp_field = self.parameterAsString(parameters, self.TIMESTAMP_FIELD, context)
        track_id = self.parameterAsInt(parameters, self.TRACK_ID, context)
        json_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        json_track = {'id': track_id, 'metadata': {'id': track_id}, 'trackPoints': list()}

        meta_number_of_points = 0
        meta_start_date = None
        meta_end_date = None
        meta_length = 0

        base_timestamp = QDateTime(QDate(1970, 1, 1), QTime(0, 0, 0), QTimeZone.utc())
        base_timestamp_sec = base_timestamp.toMSecsSinceEpoch()

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feature in enumerate(source.getFeatures()):

            # geometry = feature.geometry().asPoint()

            feature_timestamp_sec = feature[timestamp_field].toMSecsSinceEpoch()
            timestamp = int((feature_timestamp_sec - base_timestamp_sec))

            meta_start_date = timestamp if meta_start_date is None else meta_start_date
            meta_end_date = timestamp
            meta_number_of_points += 1

            json_track['trackPoints'].append({'timestamp': timestamp,
                                              'x': feature.geometry().constGet().x(),
                                              'y': feature.geometry().constGet().y(),
                                              'z': feature.geometry().constGet().z()})
            feedback.setProgress(int(current * total))

        json_track['metadata']['duration'] = meta_end_date - meta_start_date
        json_track['metadata']['startDate'] = meta_start_date
        json_track['metadata']['endDate'] = meta_end_date
        json_track['metadata']['length'] = meta_length
        json_track['metadata']['numberOfPoints'] = meta_number_of_points

        with open(json_file, 'w') as output_file:
            output_file.write(json.dumps(json_track))

        return {
            self.OUTPUT: json_file,
            self.NUMBER_TRACK_POINTS: meta_number_of_points
        }
