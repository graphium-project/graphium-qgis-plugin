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

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QFont


class TableGraphNameModel(QAbstractTableModel):
    """ Data model for the attribute table """

    def __init__(self, data_in, header_data, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        super(TableGraphNameModel, self).__init__()
        self._array_data = data_in
        self._header_data = header_data
        self.default_graph_name_index = -1

    def rowCount(self, parent=None, *args):
        return len(self._array_data)

    def columnCount(self, parent=None, *args):
        return 2

    def headerData(self, column, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header_data[column]
        # return ""
        return QAbstractTableModel.headerData(self, column, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        """
        Write data into the table
        :param index:
        :param role:
        :return:
        """
        if not index.isValid():
            return ""
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return self._array_data[index.row()]['name']
            elif index.column() == 1:
                return self._array_data[index.row()]['graph_version_count']
        elif role == Qt.FontRole:
            if self.default_graph_name_index >= 0 and index.row() == self.default_graph_name_index:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """
        Reads edited data from the table
        :param index:
        :param value:
        :param role:
        :return:
        """
        if not index.isValid():
            return ""
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return QAbstractTableModel.flags(self, index) | Qt.NoItemFlags
