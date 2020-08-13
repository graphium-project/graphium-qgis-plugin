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

import urllib.request
import urllib.error
import urllib.parse
import requests
import os.path
import json
# PyQt
from qgis.PyQt.QtCore import (QUrlQuery)
# Graphium
from .graphium_api import (GraphiumApi)


class GraphiumGraphManagementApi(GraphiumApi):
    """
    sources:
     - https://qgis.org/pyqgis/3.12/core/QgsNetworkAccessManager.html
     - https://qgis.org/pyqgis/3.12/core/QgsNetworkReplyContent.html
     - https://doc.qt.io/qt-5/qnetworkaccessmanager.html
     - https://doc.qt.io/qt-5/qnetworkrequest.html
     - https://doc.qt.io/qt-5/qnetworkreply.html
     - https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum
    """

    def __init__(self, feedback=None):
        super(GraphiumGraphManagementApi, self).__init__(feedback)

    def get_graph_names(self, return_function=None):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/metadata/graphs'

        response = self.process_get_call(url, None)

        if return_function is not None:
            return_function([] if response == '' else response)
        else:
            return [] if response == '' else response

    def get_graph_versions(self, graph_name, state_filter=None, return_function=None):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/metadata/graphs/' + graph_name + '/versions'
        versions = self.process_get_call(url, None)

        if state_filter is not None:
            versions_filtered = []
            for version in versions:
                if version.get('state') == state_filter:
                    versions_filtered.append(version)
            versions = versions_filtered

        if return_function is not None:
            return_function(versions)
        else:
            return versions

    def add_graph_version_new(self, new_graph_file, graph_name, graph_version, is_hd_segments, override_if_exists):
        if self.connection is None:
            return {"error": {"msg": "No connection selected"}}

        url = self.connection.get_connection_url() + '/' + ('hdwaysegments' if is_hd_segments else 'segments') + \
            '/graphs/' + graph_name + '/versions/' + graph_version

        url_query_items = QUrlQuery()
        url_query_items.addQueryItem('overrideIfExists', str(override_if_exists))

        return self.process_post_call(url, url_query_items, new_graph_file)

    def add_graph_version(self, new_graph_file, graph_name, graph_version, is_hd_segments, override_if_exists):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/' + ('hdwaysegments' if is_hd_segments else 'segments') + \
            '/graphs/' + graph_name + '/versions/' + graph_version

        self.report_info('POST ' + url)

        params = {"overrideIfExists": override_if_exists}

        try:
            with open(new_graph_file, 'r') as f:
                response = requests.post(url, data=params, files={'file': f})  # , headers=headers)

        except urllib.error.HTTPError as e:
            print("HTTP error: %d" % e.code)
            return None
        except urllib.error.URLError as e:
            print("Network error: %s" % e.reason.args[1])
            return None

        if response.status_code == 404:
            return {"error": {"msg": "404 ContentNotFoundError"}}
        elif response.status_code == 500:
            response_json = response.json()
            return {"error": {"msg": '500 ' + response_json['exception'] + ' - ' + response_json['message']}}
        elif response.status_code != 200:
            response_json = response.json()
            return {"error": {"msg": str(response.status_code) + ' ' + response_json['exception'] + ' - ' +
                                     response_json['message']}}
        else:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                self.report_error("JSON Decode Error from position " + str(e.pos), True)
                return {"error": {"msg": "JSON Decode Error from position " + str(e.pos)}}

    def remove_graph_version(self, graph_name, graph_version, is_hd_segments=False, keep_metadata=True):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/' + ('hdwaysegments' if is_hd_segments else 'segments') +\
              '/graphs/' + graph_name + '/versions/' + graph_version + \
              '?keepMetadata=' + str(keep_metadata)

        # url_query_items = QUrlQuery()
        # url_query_items.addQueryItem('keepMetadata', str(keep_metadata))

        return self.process_delete_call(url)

    def modify_graph_version_attribute(self, graph_name, graph_version, attribute, value):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/metadata/graphs/' + graph_name + '/versions/' + graph_version + \
            '/' + attribute + '/' + value

        return self.process_put_call(url, value)

    def do_change_detection(self, graph_name, graph_version_a, graph_version_b):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/changes/graphs/' + graph_name + '/from/' + graph_version_a + \
              '/to/' + graph_version_b + '/dodetect'
        return self.process_get_call(url, None)

    def get_changesets(self, graph_name):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/changes/graphs/' + graph_name
        return self.process_get_call(url, None)

    def get_changeset_changes(self, graph_name, graph_version_a, graph_version_b):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + \
            '/changes/graphs/' + graph_name + '/from/' + graph_version_a + '/to/' + graph_version_b
        return self.process_get_call(url, None)
