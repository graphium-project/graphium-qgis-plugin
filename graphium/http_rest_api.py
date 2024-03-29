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
import base64
from requests import Timeout
# PyQt imports
from qgis.PyQt.QtCore import (QUrl, QEventLoop)
from qgis.PyQt.QtNetwork import (QNetworkRequest, QNetworkReply)
from qgis.PyQt.QtCore import (QJsonDocument)
# qgis imports
from qgis.core import (QgsApplication, QgsNetworkAccessManager, QgsAuthMethodConfig)
# Graphium
from .settings import Settings


class HttpRestApi:
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
        self.network_access_manager = QgsNetworkAccessManager.instance()
        self.network_access_manager.downloadProgress.connect(self.download_progress)
        self.network_access_manager.authenticationRequired.connect(self.authenticate)
        self.connection = None
        self.feedback = feedback
        self.settings = Settings()
        self.auth = 0

        self.network_access_manager.setTimeout(self.settings.get_timeout_sec() * 1000)

    def process_get_call(self, url, url_query_items, timeout=None, report_url=True):
        """
        Run a GET request and return reply data
        :param url: url for request
        :param url_query_items:
        :param timeout: in ms
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        url_query = QUrl(url)
        if report_url:
            self.report_info('GET ' + url_query.toString())

        if url_query_items:
            url_query.setQuery(url_query_items)

        request = QNetworkRequest(url_query)
        if self.connection.auth_cfg != '':
            request.setRawHeader("Accept".encode("utf-8"), "*/*".encode("utf-8"))
        if timeout is not None and "setTransferTimeout" in dir(request):
            request.setTransferTimeout(timeout)

        reply = self.network_access_manager.blockingGet(request, self.connection.auth_cfg, True, self.feedback)
        return self.process_qgs_reply(reply)

    def process_post_call(self, url, url_query_items, data, is_read_only=True, report_url=True):
        """
        Run a POST request and return reply data
        :param url: url for request
        :param url_query_items:
        :param data:
        :param is_read_only: True if the request does not update data
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        if self.connection.read_only and not is_read_only:
            return {"error": {"msg": "Graphium connection is set to read-only!"}}

        url_query = QUrl(url)
        if report_url:
            self.report_info('POST ' + url_query.toString())

        if url_query_items:
            url_query.setQuery(url_query_items)

        # data_byte_array = json.dumps(data).encode('utf8')
        # data = QtCore.QByteArray( json.dumps( json_request ) )
        data_byte_array = QJsonDocument.fromVariant(data)

        request = QNetworkRequest(url_query)
        if self.connection.auth_cfg != '':
            request.setRawHeader("Accept".encode("utf-8"), "*/*".encode("utf-8"))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        reply = self.network_access_manager.blockingPost(request, data_byte_array.toJson(), self.connection.auth_cfg,
                                                         True, self.feedback)
        return self.process_qgs_reply(reply)

    def process_put_call_using_requests(self, url, data=None, report_url=True):
        """
        Deprecated
        Run a PUT request and return reply data
        :param url: url for request
        :param data:
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        if self.connection.read_only:
            return {"error": {"msg": "Graphium connection is set to read-only!"}}

        if report_url:
            self.report_info('PUT ' + url)

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

    def process_put_call(self, url, data=None, report_url=True):
        """
        Run a PUT request and return reply data
        :param url: url for request
        :param data:
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        if self.connection.read_only:
            return {"error": {"msg": "Graphium connection is set to read-only!"}}

        url_query = QUrl(url)
        if report_url:
            self.report_info('PUT ' + url_query.toString())

        data_byte_array = QJsonDocument.fromVariant(data)

        request = QNetworkRequest(url_query)
        if self.connection.auth_cfg != '':
            self.auth = 0
            config = QgsAuthMethodConfig()
            QgsApplication.authManager().loadAuthenticationConfig(self.connection.auth_cfg, config, True)
            concatenated = config.configMap()['username'] + ":" + config.configMap()['password']

            data = base64.encodebytes(concatenated.encode("utf-8")).replace('\n'.encode("utf-8"), ''.encode("utf-8"))
            request.setRawHeader("Authorization".encode("utf-8"), ("Basic %s" % data).encode("utf-8"))
            request.setRawHeader("Accept".encode("utf-8"), "*/*".encode("utf-8"))
        loop = QEventLoop()  # https://stackoverflow.com/a/46514984
        reply = self.network_access_manager.put(request, data_byte_array.toJson())
        reply.finished.connect(loop.quit)
        loop.exec_()

        return self.process_q_reply(reply)

    def process_delete_call_using_requests(self, url, report_url=True):
        """
        Deprecated
        Run a DELETE request and return reply data
        :param url: url for request
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        if self.connection.read_only:
            return {"error": {"msg": "Graphium connection is set to read-only!"}}

        if report_url:
            self.report_info('DELETE ' + url)

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

    def process_delete_call(self, url, report_url=True):
        """
        Run a DELETE request and return reply data
        :param url: url for request
        :param report_url: True if URL should be reported to feedback
        :return: response or error message in json format
        """

        if self.connection.read_only:
            return {"error": {"msg": "Graphium connection is set to read-only!"}}

        url_query = QUrl(url)
        if report_url:
            self.report_info('DELETE ' + url_query.toString())

        request = QNetworkRequest(url_query)
        if self.connection.auth_cfg != '':
            self.auth = 0
            config = QgsAuthMethodConfig()
            QgsApplication.authManager().loadAuthenticationConfig(self.connection.auth_cfg, config, True)
            concatenated = config.configMap()['username'] + ":" + config.configMap()['password']

            data = base64.encodebytes(concatenated.encode("utf-8")).replace('\n'.encode("utf-8"), ''.encode("utf-8"))
            request.setRawHeader("Authorization".encode("utf-8"), ("Basic %s" % data).encode("utf-8"))
            request.setRawHeader("Accept".encode("utf-8"), "*/*".encode("utf-8"))
        loop = QEventLoop()
        reply = self.network_access_manager.deleteResource(request)
        reply.finished.connect(loop.quit)
        loop.exec_()

        return self.process_q_reply(reply)

    def authenticate(self, reply, auth):
        """
        :param reply:
        :param auth:
        :return:
        """

        if not self.connection:
            self.report_error("No connection set for authentication!")
            reply.abort()

        if self.connection.auth_cfg == '':
            return

        self.report_info('Authenticating connection \'' + self.connection.name + '\' with auth_cfg \'' +
                         str(self.connection.auth_cfg) + '\'')
        self.auth += 1
        if self.auth >= 3:
            reply.abort()

        config = QgsAuthMethodConfig()
        QgsApplication.authManager().loadAuthenticationConfig(self.connection.auth_cfg, config, True)
        if 'username' in config.configMap():
            auth.setUser(config.configMap()['username'])
            auth.setPassword(config.configMap()['password'])

    def update_progress(self, sent, total):
        if self.feedback:
            self.feedback.setProgress(int(sent * total))

    def download_progress(self, request_id, received, total):
        if self.feedback and total != -1:
            self.feedback.setProgress(int(received * total))

    def process_q_reply(self, reply):
        reply_content = self.process_reply(reply, reply.readAll())
        reply.deleteLater()
        return reply_content

    def process_qgs_reply(self, reply):
        return self.process_reply(reply, reply.content())

    def process_reply(self, reply, reply_content):
        if reply.error() == QNetworkReply.NoError:
            header_content_type_label = 'Content-Type'
            if reply.hasRawHeader(header_content_type_label.encode('utf8')):
                header_content_type_value = reply.rawHeader(header_content_type_label.encode('utf8')).data().decode(
                    'utf8')
                header_content_type = header_content_type_value.split(';')
                content_type = header_content_type[0].strip()
                if len(header_content_type) > 1:
                    # TODO use this (currently raises LookupError)
                    charset = header_content_type[1].strip().replace('-', '').lower()
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
            return {"error": {"msg": '404 ContentNotFoundError'}}
        elif reply.error() == QNetworkReply.InternalServerError:
            return {"error": {"msg": '500 InternalServerError - ' + reply.errorString()}}
        elif reply.error() == QNetworkReply.AuthenticationRequiredError:
            return {"error": {"msg": 'AuthenticationRequiredError'}}
        else:
            return {"error": {"msg": reply.errorString()}}

    def report_error(self, message, fatal_error=False):
        if self.feedback is not None:
            self.feedback.reportError(message, fatal_error)
        else:
            print(message)

    def report_info(self, message):
        if self.feedback is not None:
            self.feedback.pushInfo(message)
        else:
            print(message)

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
        """
        Checks the connection
        to be overridden in child implementation
        :return:
        """
        return False
