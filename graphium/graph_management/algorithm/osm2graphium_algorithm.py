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
import subprocess
# PyQt imports
from qgis.PyQt.QtCore import (QCoreApplication, QSettings)
from qgis.PyQt.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterBoolean, QgsProcessingAlgorithm,
                       QgsProcessingParameterString, QgsProcessingParameterEnum)
# plugin imports
from ..model.osm_highway_types import OsmHighwayTypes
from ...settings import Settings
from ...connection.graphium_connection_manager import GraphiumConnectionManager


class Osm2GraphiumAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to convert a OpenStreetMap graph file into Graphium JSON format.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Management"
        self.alg_group_id = "graphmanagement"
        self.alg_name = "osm2graphiumconverter"
        self.alg_display_name = "OSM to Graphium converter"

        self.INPUT_JAVA = 'INPUT_JAVA'
        self.INPUT_OSM2GRAPHIUM = 'INPUT_OSM2GRAPHIUM'
        self.INPUT = 'INPUT'
        self.SERVER_NAME = 'SERVER_NAME'
        self.GRAPH_NAME = 'GRAPH_NAME'
        self.GRAPH_VERSION = 'GRAPH_VERSION'
        self.VALID_FROM = 'VALID_FROM'
        self.VALID_TO = 'VALID_TO'
        self.BOUNDS = 'BOUNDS'
        self.USE_HIGHWAY_TYPES = 'USE_HIGHWAY_TYPES'
        self.HIGHWAY_TYPES = 'HIGHWAY_TYPES'
        self.TAGS = 'TAGS'
        # self.KEEP_DOWNLOADED_FILE = 'KEEP_DOWNLOADED_FILE'
        # self.FORCE_DOWNLOAD = 'FORCE_DOWNLOAD'
        self.KEEP_CONVERTED_FILE = 'KEEP_CONVERTED_FILE'
        self.OVERRIDE_IF_EXISTS = 'OVERRIDE_IF_EXISTS'
        self.OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
        self.OUTPUT_JSON = 'OUTPUT_JSON'

        self.valid_timestamp_format = '%Y-%m-%d %H:%M'
        self.highway_options = []
        self.highway_option_values = []
        for highway_type in OsmHighwayTypes:
            self.highway_options.append(highway_type.name)
            self.highway_option_values.append(highway_type.value)
        self.tags_options = ['none', 'all']

        self.connection_manager = GraphiumConnectionManager()
        self.server_name_options = list()

    def createInstance(self):
        return Osm2GraphiumAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to convert a road network within a OSM graph file into Graphium JSON'
                       'format.')

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
        source_java = QSettings().value('plugin-graphium/java_exe', '')
        self.addParameter(QgsProcessingParameterFile(self.INPUT_JAVA,
                                                     self.tr('Java Runtime Environment (JRE) file'),
                                                     0, 'exe', source_java, False))
        source_osm2graphium = QSettings().value('plugin-graphium/osm2graphium_jar', '')
        self.addParameter(QgsProcessingParameterFile(self.INPUT_OSM2GRAPHIUM,
                                                     self.tr('OSM2Graphium JAR file'),
                                                     0, 'jar', source_osm2graphium, False))
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('OpenStreetMap file'),
                                                     # QgsProcessingParameterFile.Behavior.File, '*.gpx',
                                                     # >1 extension not possible (QGIS Dev Vol 154 Issue 49 Message 3)
                                                     0, 'pbf', None, False, "*.osm;*.pbf"))

        # read server connections and prepare enum items
        self.server_name_options.clear()
        self.server_name_options.append("[Do not import the converted file to the server]")
        selected_graph_server = Settings.get_selected_graph_server()
        selected_index = 0
        for index, connection in enumerate(self.connection_manager.read_connections()):
            self.server_name_options.append(connection.name)
            if selected_index == 0 and isinstance(selected_graph_server, str)\
                    and connection.name == selected_graph_server:
                selected_index = index + 1
        self.addParameter(QgsProcessingParameterEnum(self.SERVER_NAME, self.tr('Server name'),
                                                     self.server_name_options, False, selected_index, False))

        s = Settings.get_selected_graph_name()
        default_graph_name = ''
        if isinstance(s, str):
            default_graph_name = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_NAME, self.tr('Graph name'),
                                                       default_graph_name, False, False))
        s = Settings.get_selected_graph_version()
        default_graph_version = ''
        if isinstance(s, str):
            default_graph_version = s
        self.addParameter(QgsProcessingParameterString(self.GRAPH_VERSION, self.tr('Graph version'),
                                                       default_graph_version, False, False))

        default_valid_from = datetime.today().strftime(self.valid_timestamp_format)
        self.addParameter(QgsProcessingParameterString(self.VALID_FROM, self.tr('Valid from'),
                                                       default_valid_from, False, True))

        self.addParameter(QgsProcessingParameterString(self.VALID_TO, self.tr('Valid to'),
                                                       '', False, True))

        # self.addParameter(QgsProcessingParameterExtent(self.BOUNDS, self.tr('Bounding box'), True))

        self.addParameter(QgsProcessingParameterBoolean(self.USE_HIGHWAY_TYPES, self.tr('Use highway types'),
                                                        True, False))

        self.addParameter(QgsProcessingParameterEnum(self.HIGHWAY_TYPES, self.tr('Highway types'),
                                                     self.highway_options, True, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], False))

        self.addParameter(QgsProcessingParameterEnum(self.TAGS, self.tr('Tags'), self.tags_options, False, 0, True))

        # self.addParameter(QgsProcessingParameterBoolean(self.KEEP_DOWNLOADED_FILE, self.tr('Keep downloaded file'),
        #                                                 True, True))
        #
        # self.addParameter(QgsProcessingParameterBoolean(self.FORCE_DOWNLOAD, self.tr('Force download'),
        #                                                 False, True))

        self.addParameter(QgsProcessingParameterBoolean(self.KEEP_CONVERTED_FILE, self.tr('Keep converted file'),
                                                        True, True))

        self.addParameter(QgsProcessingParameterBoolean(self.OVERRIDE_IF_EXISTS,
                                                        self.tr('Override graph version if it exists on server'),
                                                        True, True))

        output_dir = QSettings().value('plugin-graphium/osm2graphium_output_dir', '')
        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_DIRECTORY, self.tr('Output directory'),
                                                     QgsProcessingParameterFile.Folder, defaultValue=output_dir,
                                                     optional=False))

    def checkParameterValues(self, parameters, context):
        ok, message = super(Osm2GraphiumAlgorithm, self).checkParameterValues(parameters, context)
        if ok:
            source_java = self.parameterAsFile(parameters, self.INPUT_JAVA, context)
            if source_java != '':
                if not os.path.isfile(source_java):
                    ok, message = False, 'Cannot find JRE file!'
            source_osm2graphium = self.parameterAsFile(parameters, self.INPUT_OSM2GRAPHIUM, context)
            if source_osm2graphium != '':
                if not os.path.isfile(source_osm2graphium):
                    ok, message = False, 'Cannot find OSM2Graphium converter file!'
            source = self.parameterAsFile(parameters, self.INPUT, context)
            if source != '':
                if not os.path.isfile(source):
                    ok, message = False, 'Cannot find OSM file!'
            output_directory = self.parameterAsFileOutput(parameters, self.OUTPUT_DIRECTORY, context)
            if output_directory != '':
                if not os.path.isdir(output_directory):
                    ok, message = False, 'Cannot find output directory!'
            valid_from = self.parameterAsString(parameters, self.VALID_FROM, context)
            if valid_from != '':
                try:
                    datetime.strptime(valid_from, self.valid_timestamp_format)
                except ValueError:
                    ok, message = False, 'Cannot parse valid_from (format ' + self.valid_timestamp_format + ')'
            valid_to = self.parameterAsString(parameters, self.VALID_TO, context)
            if valid_to != '':
                try:
                    datetime.strptime(valid_to, self.valid_timestamp_format)
                except ValueError:
                    ok, message = False, 'Cannot parse valid_to (format ' + self.valid_timestamp_format + ')'

        return ok, message

    def processAlgorithm(self, parameters, context, feedback):
        # pass
        source_java = self.parameterAsFile(parameters, self.INPUT_JAVA, context)
        source_osm2graphium = self.parameterAsFile(parameters, self.INPUT_OSM2GRAPHIUM, context)
        source = self.parameterAsFile(parameters, self.INPUT, context)
        server_name_index = self.parameterAsEnum(parameters, self.SERVER_NAME, context)
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)
        valid_from = self.parameterAsString(parameters, self.VALID_FROM, context)
        valid_to = self.parameterAsString(parameters, self.VALID_TO, context)
        # boundingbox = self.parameterAsExtent(parameters, self.BOUNDS, context)
        use_highway_types = self.parameterAsBoolean(parameters, self.USE_HIGHWAY_TYPES, context)
        highway_type_indexes = self.parameterAsEnums(parameters, self.HIGHWAY_TYPES, context)
        tags = self.tags_options[self.parameterAsInt(parameters, self.TAGS, context)]
        # keep_downloaded_file = self.parameterAsBoolean(parameters, self.KEEP_DOWNLOADED_FILE, context)
        # force_download = self.parameterAsBoolean(parameters, self.FORCE_DOWNLOAD, context)
        keep_converted_file = self.parameterAsBoolean(parameters, self.KEEP_CONVERTED_FILE, context)
        overrides_if_exists = self.parameterAsBoolean(parameters, self.OVERRIDE_IF_EXISTS, context)
        output_directory = self.parameterAsFileOutput(parameters, self.OUTPUT_DIRECTORY, context)

        QSettings().setValue("plugin-graphium/java_exe", source_java)
        QSettings().setValue("plugin-graphium/osm2graphium_jar", source_osm2graphium)
        QSettings().setValue("plugin-graphium/osm2graphium_output_dir", output_directory)

        server_name = self.server_name_options[server_name_index] if server_name_index > 0 else None
        selected_connection = None
        if server_name is not None:
            selected_connection = self.connection_manager.select_graphium_server(server_name)
        # bounds = boundingbox.xMinimum()

        highway_types = '"'
        for index, highway_type_index in enumerate(highway_type_indexes):
            highway_types += ', ' if index > 0 else ''
            highway_types += str(self.highway_option_values[highway_type_index])
        highway_types += '"'

        args = [source_java, '-jar', source_osm2graphium,
                '-i', source, '-o', output_directory,
                '-n', graph_name, '-v', graph_version]
        if valid_from != '':
            args.extend(['-vf', valid_from])
        if valid_to != '':
            args.extend(['-vt', valid_to])
        if use_highway_types:
            args.extend(['--highwayTypes', highway_types])
        # '--valid-from', valid_from, '--valid-to', valid_to,
        args.extend(['--tags', tags])
        # '	--downloadDir',
        # args.extend(['--keepDownloadFile', str(keep_downloaded_file),
        #              '--forceDownload', str(force_download)])
        args.extend(['--keepConvertedFile', str(keep_converted_file)])
        if selected_connection:
            url = selected_connection.get_connection_url() + "/segments/graphs/" + graph_name + "/versions/" +\
                  graph_version + "?overrideIfExists=" + str(overrides_if_exists)
            args.extend(['--importUrl', url])

        feedback.pushInfo(' '.join([str(elem) for elem in args]))
        feedback.pushInfo('This process will take several minutes...')

        try:
            process = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            try:
                out = process.stdout.decode('utf-8')
                if out:
                    feedback.pushInfo(out)
            except UnicodeDecodeError:
                feedback.reportError("Cannot decode response!")

            return {self.OUTPUT_DIRECTORY: output_directory,
                    self.OUTPUT_JSON: output_directory + '/' + graph_name + '_' + graph_version + '.json'}
        except subprocess.CalledProcessError as e:
            feedback.reportError('Return code ' + str(e.returncode), True)
            feedback.reportError(str(e), True)

        return {}
