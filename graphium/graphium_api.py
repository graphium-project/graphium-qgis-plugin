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
import json
import requests
import time
# PyQt imports
from qgis.PyQt.QtCore import (QUrl, QSettings)
from qgis.PyQt.QtNetwork import (QNetworkRequest, QNetworkReply)
from qgis.PyQt.QtCore import (QJsonDocument)
# qgis imports
from qgis.core import (QgsNetworkAccessManager)
# Graphium
from requests import Timeout


class GraphiumApi:
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
        self.network_access_manager = QgsNetworkAccessManager.instance()
        self.connection = None
        self.feedback = feedback

        self.timeout_sec = int(QSettings().value('plugin-graphium/timeout_sec', -1))
        if self.timeout_sec == -1:
            QSettings().setValue("plugin-graphium/timeout_sec", 60*10)
        self.timeout_sec = int(QSettings().value('plugin-graphium/timeout_sec', 60*10))

    def process_get_call(self, url, url_query_items):
        """
        :param url:
        :param url_query_items:
        :return: response or error message in json format
        """

        url_query = QUrl(url)
        self.report_info(url_query.toString())

        if url_query_items:
            url_query.setQuery(url_query_items)

        request = QNetworkRequest(url_query)
        self.network_access_manager.setTimeout(self.timeout_sec * 1000)
        # network_access_manager.downloadProgress.connect(self.download_progress)
        reply = self.network_access_manager.blockingGet(request, '', True)  # , self.feedback)
        return self.process_qgs_reply(reply)

    def process_post_call(self, url, url_query_items, data):
        """
        :param url:
        :param url_query_items:
        :param data:
        :return: response or error message in json format
        """

        url_query = QUrl(url)
        self.report_info(url_query.toString())

        if url_query_items:
            url_query.setQuery(url_query_items)

        # data_byte_array = json.dumps(data).encode('utf8')
        # data = QtCore.QByteArray( json.dumps( json_request ) )  # https://www.programcreek.com/python/example/82673/PyQt4.QtNetwork.QNetworkRequest
        data_byte_array = QJsonDocument.fromVariant(data)

        request = QNetworkRequest(url_query)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.network_access_manager.setTimeout(self.timeout_sec * 1000)
        # network_access_manager.uploadProgress.connect(self.update_progress)
        # network_access_manager.downloadProgress.connect(self.download_progress)
        reply = self.network_access_manager.blockingPost(request, data_byte_array.toJson(), '', True)  # , self.feedback)
        return self.process_qgs_reply(reply)

    def process_put_call(self, url, data=None):

        self.report_info(url)

        try:
            response = requests.put(url)
        except urllib.error.HTTPError as e:
            self.report_error("HTTP error: %d" % e.code, True)
            return None
        except urllib.error.URLError as e:
            self.report_error("Network error: %s" % e.reason.args[1], True)
            return None
        except Timeout:
            self.report_error("Timeout", True)
            return {"error": {"msg": "Timeout"}}

        if response.status_code == 404:
            return {"error": {"msg": "ContentNotFoundError"}}
        elif response.status_code == 422:
            return {"error": {"msg": "UnprocessableEntity"}}
        elif response.status_code != 200:
            return {"error": {"msg": "Status code: " + str(response.status_code) + ", Reason: " + response.reason}}
        else:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                self.report_error("JSONDecodeError: %s" % e.msg, True)
                self.report_error("JSON: %s" % str(response.text), True)
                return {"error": {"msg": "JSON Decode Error"}}

    def process_put_call_new(self, url, data=None):
        """
        :param url:
        :param data:
        :return: reply object
        """

        url_query = QUrl(url)
        self.report_info(url_query.toString())

        data_byte_array = QJsonDocument.fromVariant(data)

        request = QNetworkRequest(url_query)
        # network_access_manager.uploadProgress.connect(self.update_progress)
        self.network_access_manager.finished.connect(self.process_q_reply)
        self.reply_content = None
        reply = self.network_access_manager.put(request, data_byte_array.toJson())

        while self.reply_content is None:
            time.sleep(1)
            pass

        return self.reply_content

    def process_delete_call(self, url):
        self.report_info(url)

        try:
            response = requests.delete(url)
        except urllib.error.HTTPError as e:
            self.report_error("HTTP error: %d" % e.code, True)
            return None
        except urllib.error.URLError as e:
            self.report_error("Network error: %s" % e.reason.args[1], True)
            return None
        except Timeout:
            self.report_error("Timeout", True)
            return {"error": {"msg": "Timeout"}}

        if response.status_code == 404:
            return {"error": {"msg": "ContentNotFoundError"}}
        elif response.status_code == 422:
            return {"error": {"msg": "UnprocessableEntity"}}
        elif response.status_code != 200:
            return {"error": {"msg": "Status code: " + str(response.status_code) + ", Reason: " + response.reason}}
        else:
            if len(response.text) > 0:
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    self.report_error("JSONDecodeError: %s" % e.msg, True)
                    self.report_error("JSON: %s" % str(response.text), True)
                    return {"error": {"msg": "JSON Decode Error"}}
            else:
                return {"error": {"msg": "No error but empty response"}}

    def process_delete_call_new(self, url):
        """
        :param url:
        :return: reply object
        """

        url_query = QUrl(url)
        self.report_info(url_query.toString())

        request = QNetworkRequest(url_query)
        self.network_access_manager.downloadProgress.connect(self.update_progress)
        # network_access_manager.finished.connect(self.process_q_reply)
        reply = self.network_access_manager.deleteResource(request)

        return self.process_q_reply(reply)

    def update_progress(self, sent, total):
        if self.feedback:
            self.feedback.setProgress(int(sent * total))

    def download_progress(self, received, total):
        if self.feedback:
            self.feedback.setProgress(int(received * total))

    def process_q_reply(self, reply):
        self.reply_content = self.process_reply(reply, reply.readAll())
        return self.reply_content

    def process_qgs_reply(self, reply):
        return self.process_reply(reply, reply.content())

    def process_reply(self, reply, reply_content):
        if reply.error() == QNetworkReply.NoError:
            header_content_type_label = 'Content-Type'
            if reply.hasRawHeader(header_content_type_label.encode('utf8')):
                header_content_type_value = reply.rawHeader(header_content_type_label.encode('utf8')).data().decode('utf8')
                content_type, charset = header_content_type_value.split(';')
                content_type = content_type.strip()
                charset = charset.strip().replace('-', '').lower()  # TODO use this (currently raises LookupError)
            else:
                content_type, charset = 'application/json', 'utf8'
            if content_type == 'application/json':
                try:
                    data = reply_content.data().decode('utf8')
                    if len(data) > 0:
                        return json.loads(data)
                    else:
                        return {"error": {"msg": "No error but empty response"}}
                except json.JSONDecodeError as e:
                    self.report_error("JSON Decode Error from position " + str(e.pos), True)
                    return {"error": {"msg": "JSON Decode Error from position " + str(e.pos)}}
            else:
                data = reply_content.data().decode('utf8')
                return data
        elif reply.error() == QNetworkReply.ContentNotFoundError:
            return {"error": {"msg": 'ContentNotFoundError'}}
        else:
            return {"error": {"msg": reply.errorString()}}

    def report_error(self, message, fatal_error=False):
        if self.feedback is not None:
            self.feedback.reportError(message, fatal_error)

    def report_info(self, message):
        if self.feedback is not None:
            self.feedback.pushInfo(message)

    def connect(self, connection):
        if connection is None:
            return False

        self.connection = connection
        if self.check_connection():
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

        if capability in response:
            return True
        else:
            return False
