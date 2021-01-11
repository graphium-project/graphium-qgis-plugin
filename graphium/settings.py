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

import json
# PyQt imports
from qgis.PyQt.QtCore import QSettings


class Settings:

    plugin_id = 'plugin-graphium'

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

    def set_output_directory_default(self, output_directory_default):
        QSettings().setValue(self.plugin_id + "/output_directory_default", output_directory_default)

    def get_output_directory_default(self):
        return QSettings().value(self.plugin_id + '/output_directory_default', '')

    # graph-manager

    def set_graph_file_default_dir(self, graph_file_default_dir):
        QSettings().setValue(self.plugin_id + '/graph_file_default_dir', graph_file_default_dir)

    def get_graph_file_default_dir(self):
        return QSettings().value(self.plugin_id + '/graph_file_default_dir', '')

    # hd

    def set_hd_enabled(self, hd_enabled):
        if type(hd_enabled) is bool:
            QSettings().setValue(self.plugin_id + '/hd_enabled', hd_enabled)

    def is_hd_enabled(self) -> bool:
        hd_enabled = QSettings().value(self.plugin_id + '/hd_enabled', 'not_set')
        if hd_enabled == 'not_set':
            # set default value
            self.set_hd_enabled(False)
            hd_enabled = QSettings().value(self.plugin_id + '/hd_enabled')
        return bool(hd_enabled)

    # api

    def set_timeout_sec(self, timeout_sec):
        QSettings().setValue(self.plugin_id + '/timeout_sec', timeout_sec)

    def get_timeout_sec(self) -> int:
        timeout_sec = int(QSettings().value(self.plugin_id + '/timeout_sec', -1))
        if timeout_sec == -1:
            # set default value
            self.set_timeout_sec(60*10)
            timeout_sec = int(QSettings().value(self.plugin_id + '/timeout_sec'))
        return timeout_sec

    # map-matcher

    def set_gpx_file_default_dir(self, gpx_file_default_dir):
        QSettings().setValue(self.plugin_id + '/default_gpx_dir', gpx_file_default_dir)

    def get_gpx_file_default_dir(self):
        return QSettings().value(self.plugin_id + '/default_gpx_dir', '')

    def set_value(self, key, value):
        QSettings().setValue(self.plugin_id + '/' + key, value)

    def get_value(self, key, default_value=None):
        if QSettings().contains(self.plugin_id + '/' + key):
            return QSettings().value(self.plugin_id + '/' + key, default_value)
        else:
            QSettings().setValue(self.plugin_id + '/' + key, default_value)
            return default_value
