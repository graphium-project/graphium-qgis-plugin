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

from PyQt5.QtCore import QSettings
import json


class Settings:

    @staticmethod
    def get_locale():
        return QSettings().value('locale/userLocale', 'en_US')[0:2]

    # graphium

    @staticmethod
    def set_graphium_servers(output_list):
        QSettings().setValue("plugin-graphium/connections", json.dumps(output_list))

    @staticmethod
    def get_graphium_servers():
        return json.loads(QSettings().value('plugin-graphium/connections', "[]"))

    @staticmethod
    def set_selected_graph_version(selected_connection, selected_name, selected_version):
        QSettings().setValue("plugin-graphium/selected_graph_server", selected_connection)
        QSettings().setValue("plugin-graphium/selected_graph_name", selected_name)
        QSettings().setValue("plugin-graphium/selected_graph_version", selected_version)

    @staticmethod
    def get_selected_graph_server():
        return QSettings().value('plugin-graphium/selected_graph_server', '')

    @staticmethod
    def get_selected_graph_name():
        return QSettings().value('plugin-graphium/selected_graph_name', '')

    @staticmethod
    def get_selected_graph_version():
        return QSettings().value('plugin-graphium/selected_graph_version', '')

    @staticmethod
    def set_output_directory_default(output_directory_default):
        QSettings().setValue("graphium_qgis/output_directory_default", output_directory_default)

    @staticmethod
    def get_output_directory_default():
        return QSettings().value('graphium_qgis/output_directory_default', '')

    # graph-manager

    @staticmethod
    def set_graph_file_default_dir(graph_file_default_dir):
        QSettings().setValue("graphium_qgis/graph_file_default_dir", graph_file_default_dir)

    @staticmethod
    def get_graph_file_default_dir():
        return QSettings().value('graphium_qgis/graph_file_default_dir', '')

    # map-matcher

    @staticmethod
    def set_gpx_file_default_dir(gpx_file_default_dir):
        QSettings().setValue("graphium_qgis/default_gpx_dir", gpx_file_default_dir)

    @staticmethod
    def get_gpx_file_default_dir():
        return QSettings().value('graphium_qgis/default_gpx_dir', '')
