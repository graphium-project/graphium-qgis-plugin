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
from ..graphium_api import (GraphiumApi)


class GraphiumUtilitiesApi(GraphiumApi):
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
        super(GraphiumUtilitiesApi, self).__init__(feedback)

    def do_map_matching(self, track, graph_name, graph_version):
        if self.connection is None:
            return {"error": {"msg": "No connection selected"}}

        if not self.check_capability('mapMatching'):
            return {"error": {"msg": "Server '" + self.connection.name + "' does not support map-matching!"}}

        url = self.connection.get_connection_url() + '/graphs/' + graph_name +\
              ("/versions/current" if graph_version == 'CURRENTLY_VALID' else '') + \
              "/matchtrack?outputVerbose=true&timeoutMs=600000"

        return self.process_post_call(url, None, track)

    def do_routing(self, graph_name, graph_version, start_x, start_y, end_x, end_y, date, cut_segments, routing_mode,
                   criteria):
        if self.connection is None:
            return {"error": {"msg": "No connection selected"}}

        if not self.check_capability('routing'):
            return {"error": {"msg": "Server '" + self.connection.name + "' does not support routing!"}}

        url = self.connection.get_connection_url() + '/routing/graphs/' + graph_name + \
            '/versions/' + graph_version + '/route.do'

        url_query_items = QUrlQuery()
        url_query_items.addQueryItem('time', date.strftime("%Y-%m-%dT%H:%M:%S"))
        url_query_items.addQueryItem('coords', str(start_x) + ',' + str(start_y) + ';' + str(end_x) + ',' + str(end_y))
        url_query_items.addQueryItem('output', 'path')
        # url_query_items.addQueryItem('cutsegments', 'true' if cut_segments else 'false')
        url_query_items.addQueryItem('mode', routing_mode)
        url_query_items.addQueryItem('criteria', criteria)

        return self.process_get_call(url, url_query_items)
