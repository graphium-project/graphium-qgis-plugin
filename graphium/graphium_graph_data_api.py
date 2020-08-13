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

# PyQt
from qgis.PyQt.QtCore import (QUrlQuery)
# Graphium
from .graphium_api import (GraphiumApi)


class GraphiumGraphDataApi(GraphiumApi):
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
        super(GraphiumGraphDataApi, self).__init__(feedback)

    def get_segment(self, graph_name, graph_version, segment_id, is_hd_segments=False):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/' + ('hdwaysegments' if is_hd_segments else 'segments') +\
              '/graphs/' + graph_name + '/versions/' + graph_version

        url_query_items = QUrlQuery()
        url_query_items.addQueryItem('ids', str(segment_id))

        return self.process_get_call(url, url_query_items)

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

    def export_graph(self, graph_name, graph_version, is_hd_segments=False):
        if self.connection is None:
            return []

        url = self.connection.get_connection_url() + '/' + ('hdwaysegments' if is_hd_segments else 'segments') +\
              '/graphs/' + graph_name + '/versions/' + graph_version
        return self.process_get_call(url, None)
