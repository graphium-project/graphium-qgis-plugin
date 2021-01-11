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

from .graphium_server_type import GraphiumServerType


class Connection:

    def __init__(self, name='', server=GraphiumServerType.POSTGRES, host='http://localhost', port=None,
                 base_url='graphium/api', auth_cfg='', read_only=True):
        self.name = name
        self.server = server
        self.host = host
        self.port = port
        self.base_url = base_url
        self.auth_cfg = auth_cfg
        self.read_only = read_only

    def get_connection_url(self):
        protocol = ''
        if self.host[0:4] != 'http':
            protocol = 'http://'

        if self.port is not None:
            return protocol + self.host + ':' + str(self.port) + '/' + self.base_url
        else:
            return protocol + self.host + '/' + self.base_url

    def get_simple_url(self):
        if self.port is not None:
            return self.host + ':' + str(self.port) + '/' + self.base_url
        else:
            return self.host + '/' + self.base_url
