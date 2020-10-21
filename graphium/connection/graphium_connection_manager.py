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

from .model.graphium_connection import Connection
from .model.graphium_server_type import GraphiumServerType
from ..settings import Settings


class GraphiumConnectionManager:

    def __init__(self):
        self.connections = list()

    def save_connections(self):
        # prepare output
        server_list = list()
        for conn in self.connections:
            server_list.append([conn.name, conn.server.value, conn.host, conn.port, conn.base_url, conn.read_only])
        # write output
        Settings.set_graphium_servers(server_list)

    def read_connections(self, server_type=None):
        # read input
        connection_list = Settings.get_graphium_servers()
        # prepare connections
        self.connections = list()
        for conn in connection_list:
            if server_type is None or conn[1] == server_type.value:
                self.connections.append(Connection(conn[0], GraphiumServerType(conn[1]), conn[2], conn[3],
                                                   conn[4] if len(conn) > 4 else '',
                                                   bool(conn[5]) if len(conn) > 5 else True))
        return self.connections

    def select_graphium_server(self, server_name, server_type=None):
        self.read_connections(server_type)
        for conn in self.connections:
            if conn.name == server_name:
                return conn
