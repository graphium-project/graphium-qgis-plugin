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

# Graphium
from .http_rest_api import (HttpRestApi)


class GraphiumApi(HttpRestApi):
    """
    sources:
     - https://qgis.org/pyqgis/master/core/QgsNetworkAccessManager.html
     - https://qgis.org/pyqgis/master/core/QgsNetworkReplyContent.html
     - https://doc.qt.io/qt-5/qnetworkaccessmanager.html
     - https://doc.qt.io/qt-5/qnetworkrequest.html
     - https://doc.qt.io/qt-5/qnetworkreply.html
     - https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum
    """

    def __init__(self, feedback=None):
        super(GraphiumApi, self).__init__(feedback)

    def connect(self, connection, check=True):
        if connection is None:
            return False

        self.connection = connection
        if not check:
            return True
        elif self.check_connection():
            return True
        else:
            self.connection = None
            return False

    def disconnect(self):
        self.connection = None

    def check_connection(self):
        url = self.connection.get_connection_url() + '/status'
        response = self.process_get_call(url, None)

        if response.get('serverName'):
            return True
        else:
            return False

    def check_capability(self, capability):
        url = self.connection.get_connection_url() + '/capabilities'
        response = self.process_get_call(url, None)

        if "error" in response and response["error"]["msg"] == '404 ContentNotFoundError':
            self.report_info("Check capability not available on this server. Proceed with request...")
            return True

        if capability in response:
            return True
        else:
            return False
