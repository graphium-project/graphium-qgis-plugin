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
from ..model.access import Access
from ..model.function_road_class import FunctionalRoadClass
from ...settings import Settings
from ...connection.graphium_connection_manager import GraphiumConnectionManager


class Gip2GraphiumAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm is used to convert a GIP.at graph file into Graphium JSON format.
    """

    plugin_path = os.path.split(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0])[0]

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_group = "Graph Management"
        self.alg_group_id = "graphmanagement"
        self.alg_name = "gip2graphiumconverter"
        self.alg_display_name = "GIP to Graphium converter"

        self.INPUT_JAVA = 'INPUT_JAVA'
        self.INPUT_IDF2GRAPHIUM = 'INPUT_IDF2GRAPHIUM'
        self.INPUT = 'INPUT'
        self.SERVER_NAME = 'SERVER_NAME'
        self.GRAPH_NAME = 'GRAPH_NAME'
        self.GRAPH_VERSION = 'GRAPH_VERSION'
        self.VALID_FROM = 'VALID_FROM'
        self.VALID_TO = 'VALID_TO'
        self.IMPORT_FRCS = 'IMPORT_FRCS'
        self.ACCESS_TYPES = 'ACCESS_TYPES'
        # self.SKIP_GIP_IMPORT = 'SKIP_GIP_IMPORT'
        # self.SKIP_PIXEL_CUT = 'SKIP_PIXEL_CUT'
        # self.PIXEL_CUT_MIN_FRC = 'PIXEL_CUT_MIN_FRC'
        # self.PIXEL_CUT_MAX_FRC = 'PIXEL_CUT_MAX_FRC'
        # self.PIXEL_CUT_ENABLE_SHORT_CONN = 'PIXEL_CUT_ENABLE_SHORT_CONN'
        # self.KEEP_DOWNLOADED_FILE = 'KEEP_DOWNLOADED_FILE'
        # self.FORCE_DOWNLOAD = 'FORCE_DOWNLOAD'
        self.KEEP_CONVERTED_FILE = 'KEEP_CONVERTED_FILE'
        self.OVERRIDE_IF_EXISTS = 'OVERRIDE_IF_EXISTS'
        self.OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
        self.OUTPUT_JSON = 'OUTPUT_JSON'

        self.valid_timestamp_format = '%Y-%m-%d %H:%M'
        self.frc_options = []
        self.frc_option_values = []
        for frc in FunctionalRoadClass:
            self.frc_options.append(str(frc.value) + ' - ' + frc.name)
            self.frc_option_values.append(frc.value)
        self.access_options = []
        self.access_option_values = []
        for access in Access:
            self.access_options.append(str(access.value) + ' - ' + access.name)
            self.access_option_values.append(access.name)

        self.connection_manager = GraphiumConnectionManager()
        self.server_name_options = list()

    def createInstance(self):
        return Gip2GraphiumAlgorithm()

    def group(self):
        return self.tr(self.alg_group)

    def groupId(self):
        return self.alg_group_id

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.tr(self.alg_display_name)

    def shortHelpString(self):
        return self.tr('This algorithm is used to convert a GIP.at graph file into Graphium JSON format.')

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
        source_idf2graphium = QSettings().value('plugin-graphium/idf2graphium_jar', '')
        self.addParameter(QgsProcessingParameterFile(self.INPUT_IDF2GRAPHIUM,
                                                     self.tr('IDF2Graphium JAR file'),
                                                     0, 'jar', source_idf2graphium, False))
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('GIP.at file'),
                                                     # QgsProcessingParameterFile.Behavior.File, '*.gpx',
                                                     # >1 extension not possible (QGIS Dev Vol 154 Issue 49 Message 3)
                                                     0, 'txt', None, False, "*.txt;*.zip"))

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

        self.addParameter(QgsProcessingParameterEnum(self.IMPORT_FRCS, self.tr('Function Road Classes (FRCs)'),
                                                     self.frc_options, True, [1, 2, 3, 4, 5, 6, 7, 8, 9], False))

        self.addParameter(QgsProcessingParameterEnum(self.ACCESS_TYPES, self.tr('Access types'),
                                                     self.access_options, True, [2], False))

        # self.addParameter(QgsProcessingParameterBoolean(self.SKIP_GIP_IMPORT, self.tr('Skip GIP import'),
        #                                                 False, True))
        #
        # self.addParameter(QgsProcessingParameterBoolean(self.SKIP_PIXEL_CUT, self.tr('Skip pixel cut'),
        #                                                 True, True))
        #
        # self.addParameter(QgsProcessingParameterEnum(self.PIXEL_CUT_MIN_FRC, self.tr('Pixel cut minimum FRC'),
        #                                              self.frc_options, False, 1, True))
        #
        # self.addParameter(QgsProcessingParameterEnum(self.PIXEL_CUT_MAX_FRC, self.tr('Pixel cut maximum FRC'),
        #                                              self.frc_options, False, 5, True))
        #
        # self.addParameter(QgsProcessingParameterBoolean(self.PIXEL_CUT_ENABLE_SHORT_CONN,
        #                                                 self.tr('Enable short connections at pixel cut'), True, True))

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

        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_DIRECTORY, self.tr('Output directory'),
                                                     QgsProcessingParameterFile.Folder, optional=False))

    def checkParameterValues(self, parameters, context):
        ok, message = super(Gip2GraphiumAlgorithm, self).checkParameterValues(parameters, context)
        if ok:
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
        source_idf2graphium = self.parameterAsFile(parameters, self.INPUT_IDF2GRAPHIUM, context)
        source = self.parameterAsFile(parameters, self.INPUT, context)
        server_name = self.server_name_options[self.parameterAsInt(parameters, self.SERVER_NAME, context)]
        graph_name = self.parameterAsString(parameters, self.GRAPH_NAME, context)
        graph_version = self.parameterAsString(parameters, self.GRAPH_VERSION, context)
        valid_from = self.parameterAsString(parameters, self.VALID_FROM, context)
        valid_to = self.parameterAsString(parameters, self.VALID_TO, context)
        import_frcs_indexes = self.parameterAsEnums(parameters, self.IMPORT_FRCS, context)
        access_types_indexes = self.parameterAsEnums(parameters, self.ACCESS_TYPES, context)
        # skip_gip_import = self.parameterAsBoolean(parameters, self.SKIP_GIP_IMPORT, context)
        # skip_pixel_cut = self.parameterAsBoolean(parameters, self.SKIP_PIXEL_CUT, context)
        # pixel_cut_min_frc = self.frc_option_values[self.parameterAsInt(parameters, self.PIXEL_CUT_MIN_FRC, context)]
        # pixel_cut_max_frc = self.frc_option_values[self.parameterAsInt(parameters, self.PIXEL_CUT_MAX_FRC, context)]
        # pixel_cut_enable_short_conn = self.parameterAsBoolean(parameters, self.PIXEL_CUT_ENABLE_SHORT_CONN, context)
        # keep_downloaded_file = self.parameterAsBoolean(parameters, self.KEEP_DOWNLOADED_FILE, context)
        # force_download = self.parameterAsBoolean(parameters, self.FORCE_DOWNLOAD, context)
        keep_converted_file = self.parameterAsBoolean(parameters, self.KEEP_CONVERTED_FILE, context)
        overrides_if_exists = self.parameterAsBoolean(parameters, self.OVERRIDE_IF_EXISTS, context)
        output_directory = self.parameterAsFileOutput(parameters, self.OUTPUT_DIRECTORY, context)

        QSettings().setValue("plugin-graphium/java_exe", source_java)
        QSettings().setValue("plugin-graphium/idf2graphium_jar", source_idf2graphium)

        selected_connection = self.connection_manager.select_graphium_server(server_name)

        import_frcs = '"'
        for index, frc in enumerate(import_frcs_indexes):
            import_frcs += ',' if index > 0 else ''
            import_frcs += str(self.frc_option_values[frc])
        import_frcs += '"'

        access_types = '"'
        for index, access in enumerate(access_types_indexes):
            access_types += ',' if index > 0 else ''
            access_types += self.access_option_values[access]
        access_types += '"'

        args = [source_java, '-jar', source_idf2graphium,
                '-i', source, '-o', output_directory,
                '-n', graph_name, '-v', graph_version]
        if valid_from != '':
            args.extend(['-vf', valid_from])
        if valid_to != '':
            args.extend(['-vt', valid_to])
        if len(import_frcs_indexes) > 0:
            args.extend(['--import-frcs', import_frcs])
        if len(access_types_indexes) > 0:
            args.extend(['--access-types', access_types])
        args.append('--skip-pixel-cut')
        # '--valid-from', valid_from, '--valid-to', valid_to,
        # if skip_gip_import:
        #     args.append('--skip-gip-import')
        # if skip_pixel_cut:
        #     args.append('--skip-pixel-cut')
        # else:
        #     args.extend(['--pixel-cut-min-frc', pixel_cut_min_frc, '--pixel-cut-max-frc', pixel_cut_max_frc])
        #     if pixel_cut_enable_short_conn:
        #         args.append('--pixel-cut-enable-short-conn')
        # '--full-connectivity', 'false',
        # '	--xinfo-csv',
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
