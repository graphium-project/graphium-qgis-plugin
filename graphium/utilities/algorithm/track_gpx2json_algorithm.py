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
from datetime import datetime, timezone
# PyQt imports
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterFileDestination, QgsProcessingAlgorithm,
                       QgsProcessingOutputNumber)
# xml tools
from xml.etree import ElementTree


class TrackGpx2JsonAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to convert a trajectory GPX file into Graphium JSON format.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Utilities"
        self.alg_group_id = "graphutilities"
        self.alg_name = "gpx2jsonconverter"
        self.alg_display_name = "GPX to JSON converter"

        self.INPUT = 'INPUT'
        self.OUTPUT = 'OUTPUT'
        self.NUMBER_TRACK_POINTS = 'NUMBER_TRACK_POINTS'

        self.timestamp_formats = [
            {"format": "%Y-%m-%dT%H:%M:%SZ%z", "suffix": "+0000"},
            {"format": "%Y-%m-%dT%H:%M:%SZ%z", "suffix": ""},
            {"format": "%Y-%m-%dT%H:%M:%S.%f%z", "suffix": ""}
        ]

    def createInstance(self):
        return TrackGpx2JsonAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to convert a trajectory GPX file into Graphium JSON format.')

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
        # self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input gpx file'),
        #                                                       [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input GPX file'),
                                                     # QgsProcessingParameterFile.Behavior.File, '*.gpx',
                                                     # >1 extension not possible (QGIS Dev Vol 154 Issue 49 Message 3)
                                                     0, 'gpx', None, False))  # fileFilter="*.gpx;*.json"))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT, self.tr('Output JSON file'),
                                                                'JSON files (*.json)', optional=True))

        self.addOutput(QgsProcessingOutputNumber(self.NUMBER_TRACK_POINTS, self.tr('Number of track points')))

    def processAlgorithm(self, parameters, context, feedback):
        # pass
        source = self.parameterAsFile(parameters, self.INPUT, context)
        json_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        feedback.setProgress(0)

        tree = ElementTree.parse(source)
        root = tree.getroot()

        json_track = {'id': None, 'metadata': {}, 'trackPoints': list()}

        namespace = ''

        if root.tag[0] == "{":
            uri, ignore, tag = root.tag[1:].partition("}")
            namespace = {'gpx': uri}

        meta_number_of_points = 0
        meta_duration = 0
        meta_start_date = None
        meta_end_date = None
        meta_length = 0

        for track in root.findall('gpx:trk', namespace):

            track_number = track.find('gpx:number', namespace)
            if track_number is not None:
                json_track['id'] = int(self.normalize(track_number.text))
            else:
                json_track['id'] = int(0)

            json_track['metadata']['id'] = json_track['id']

            track_segment_list = track.findall('gpx:trkseg', namespace)
            for track_segment in track_segment_list:

                track_point_list = track_segment.findall('gpx:trkpt', namespace)
                total = 100.0 / len(track_point_list)
                for current, track_point in enumerate(track_point_list):
                    time_str = track_point.find('gpx:time', namespace)
                    timestamp = None
                    if time_str is not None:

                        gpx_timestamp = None
                        timestamp_format_index = 0
                        while gpx_timestamp is None:
                            timestamp_format = self.timestamp_formats[timestamp_format_index]
                            try:
                                gpx_timestamp = datetime.strptime(time_str.text + timestamp_format['suffix'],
                                                                  timestamp_format['format'])
                            except ValueError:
                                timestamp_format_index += 1
                                if timestamp_format_index == len(self.timestamp_formats):
                                    feedback.reportError('Cannot parse timestamp', True)
                                    return {
                                        self.OUTPUT: None,
                                        self.NUMBER_TRACK_POINTS: 0
                                    }

                        if gpx_timestamp:
                            base_timestamp = datetime(1970, 1, 1, tzinfo=timezone.utc)
                            timestamp = int((gpx_timestamp - base_timestamp).total_seconds() * 1000)

                    meta_start_date = timestamp if meta_start_date is None else meta_start_date
                    meta_end_date = timestamp
                    meta_number_of_points += 1

                    json_track['trackPoints'].append({'timestamp': timestamp,
                                                      'x': float(track_point.get('lon')),
                                                      'y': float(track_point.get('lat')),
                                                      'z': 0.0})
                    feedback.setProgress(int(current * total))

            json_track['metadata']['duration'] = meta_duration
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

    @staticmethod
    def normalize(name):
        if name[0] == '{':
            uri, tag = name[1:].split('}')
            return tag
        else:
            return name
