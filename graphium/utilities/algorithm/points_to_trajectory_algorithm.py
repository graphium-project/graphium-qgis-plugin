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
import math
import os
import json
# PyQt imports
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QDate, QTime, QTimeZone, QVariant
from qgis.PyQt.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingParameterFeatureSource, QgsProcessingParameterFileDestination, NULL,
                       QgsProcessingAlgorithm, QgsProcessingOutputNumber, QgsProcessing, QgsProcessingParameterField,
                       QgsProcessingParameterNumber, QgsProcessingParameterBoolean, QgsProcessingParameterString)
# plugin imports
from ..geom_tools import GeomTools


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
        self.TRACK_TAGS = 'TRACK_TAGS'
        self.TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
        self.ADD_MOTION_ATTRIBUTES = 'ADD_MOTION_ATTRIBUTES'
        self.FIELDS_AS_TAGS = 'FIELDS_AS_TAGS'
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

        self.addParameter(QgsProcessingParameterNumber(self.TRACK_ID, self.tr('Track ID'),
                                                       QgsProcessingParameterNumber.Integer, 0, False))

        self.addParameter(QgsProcessingParameterString(self.TRACK_TAGS, self.tr('Track Metadata Tags as JSON'),
                                                       optional=True))

        self.addParameter(QgsProcessingParameterField(self.TIMESTAMP_FIELD, self.tr('Timestamp field'),
                                                      parentLayerParameterName=self.INPUT,
                                                      type=QgsProcessingParameterField.DateTime))

        self.addParameter(QgsProcessingParameterBoolean(self.ADD_MOTION_ATTRIBUTES,
                                                        self.tr('Add motion attributes to track points'),
                                                        False, True))

        self.addParameter(QgsProcessingParameterField(self.FIELDS_AS_TAGS,
                                                      self.tr('Select fields for track point tags'),
                                                      parentLayerParameterName=self.INPUT,
                                                      allowMultiple=True, optional=True))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT, self.tr('JSON trajectory file'),
                                                                'JSON files (*.json)'))

        self.addOutput(QgsProcessingOutputNumber(self.NUMBER_TRACK_POINTS, self.tr('Number of track points')))

    def checkParameterValues(self, parameters, context):
        ok, message = super(PointsToTrajectoryAlgorithm, self).checkParameterValues(parameters, context)
        if ok:
            track_tags = self.parameterAsString(parameters, self.TRACK_TAGS, context)
            if track_tags != '':
                try:
                    json_string = json.loads(track_tags)

                    if not isinstance(json_string, dict):
                        ok, message = False, 'TRACK_TAGS must be a dict object (currently ' + str(type(json_string)) +\
                                      ')'

                except json.JSONDecodeError:
                    ok, message = False, 'Cannot parse TRACK_TAGS JSON'

        return ok, message

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        track_id = self.parameterAsInt(parameters, self.TRACK_ID, context)
        track_tags = self.parameterAsString(parameters, self.TRACK_TAGS, context)
        timestamp_field = self.parameterAsString(parameters, self.TIMESTAMP_FIELD, context)
        add_track_point_motion_attributes = self.parameterAsBoolean(parameters, self.ADD_MOTION_ATTRIBUTES, context)
        fields_for_tags = self.parameterAsFields(parameters, self.FIELDS_AS_TAGS, context)
        json_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        json_track = {'id': track_id, 'metadata': dict(), 'trackPoints': list()}

        meta_number_of_points = 0
        meta_start_date = None
        meta_end_date = None
        meta_length = 0
        meta_tags = None
        if track_tags != '':
            meta_tags = json.loads(track_tags)

        base_timestamp = QDateTime(QDate(1970, 1, 1), QTime(0, 0, 0), QTimeZone.utc())
        base_timestamp_sec = base_timestamp.toMSecsSinceEpoch()

        previous_feature = None
        previous_track_point = None

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feature in enumerate(source.getFeatures()):

            # geometry = feature.geometry().asPoint()

            feature_timestamp_sec = feature[timestamp_field].toMSecsSinceEpoch()
            timestamp = int((feature_timestamp_sec - base_timestamp_sec))

            meta_start_date = timestamp if meta_start_date is None else meta_start_date
            meta_end_date = timestamp
            meta_number_of_points += 1

            track_point = {
                'id': meta_number_of_points,
                't': timestamp,
                'x': feature.geometry().constGet().x(),
                'y': feature.geometry().constGet().y(),
                'z': feature.geometry().constGet().z()}

            if previous_feature:
                length = GeomTools.distance(previous_feature.geometry().constGet(),
                                            feature.geometry().constGet(), source.sourceCrs())
                if length is not None:
                    meta_length += length

            if add_track_point_motion_attributes:
                if previous_feature:
                    track_point['h'] = GeomTools.calculate_angle(previous_feature.geometry().constGet(),
                                                                 feature.geometry().constGet()) / math.pi * 180
                    track_point['distCalc'] = length
                    track_point['vCalc'] = GeomTools.calculate_speed(previous_feature[timestamp_field],
                                                                     feature[timestamp_field],
                                                                     previous_feature.geometry().constGet(),
                                                                     feature.geometry().constGet(),
                                                                     source.sourceCrs())
                    track_point['durationCalc'] = timestamp - previous_track_point['t']
                    if track_point['vCalc'] and previous_track_point['vCalc']:
                        track_point['aCalc'] = (track_point['vCalc'] / 3.6 - previous_track_point['vCalc'] / 3.6) /\
                                               (track_point['durationCalc'] / 1000)
                    else:
                        track_point['aCalc'] = None
                else:
                    # first feature
                    track_point['h'] = None
                    track_point['distCalc'] = None
                    track_point['vCalc'] = None
                    track_point['durationCalc'] = None
                    track_point['aCalc'] = None

            if len(fields_for_tags) > 0:
                track_point_tags = dict()
                for field in fields_for_tags:
                    if feature[field]:
                        track_point_tags[field] = feature[field]

                if len(track_point_tags) > 0:
                    track_point['tags'] = track_point_tags

            json_track['trackPoints'].append(track_point)
            feedback.setProgress(int(current * total))

            previous_feature = feature
            previous_track_point = track_point

        json_track['metadata']['duration'] = meta_end_date - meta_start_date
        json_track['metadata']['startDate'] = meta_start_date
        json_track['metadata']['endDate'] = meta_end_date
        json_track['metadata']['length'] = meta_length
        json_track['metadata']['numberOfPoints'] = meta_number_of_points
        if meta_tags:
            json_track['metadata']['tags'] = meta_tags

        with open(json_file, 'w') as output_file:
            output_file.write(json.dumps(json_track))

        return {
            self.OUTPUT: json_file,
            self.NUMBER_TRACK_POINTS: meta_number_of_points
        }
