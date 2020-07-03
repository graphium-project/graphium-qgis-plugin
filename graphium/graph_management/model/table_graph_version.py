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
from datetime import datetime


class TableGraphVersionModel(QAbstractTableModel):
    """ Data model for the attribute table """

    date_format = '%Y-%m-%d %H:%M:%S'
    date_read_format = '%Y-%m-%d %H:%M:%S%z'

    def __init__(self, data_in, header_data, update_graph_version_validity,  parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        # QAbstractTableModel.__init__(self, parent, *args)
        super(TableGraphVersionModel, self).__init__()
        self._array_data = data_in
        self._header_data = header_data
        self.default_graph_version_index = -1
        self.update_graph_version_validity = update_graph_version_validity

    def rowCount(self, parent=None, *args):
        return len(self._array_data)

    def columnCount(self, parent=None, *args):
        return 6

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
                return self._array_data[index.row()]['id']
            elif index.column() == 1:
                return self._array_data[index.row()]['version']
            elif index.column() == 2:
                return self._array_data[index.row()]['type']
            elif index.column() == 3:
                return self._array_data[index.row()]['state']
            elif index.column() == 4:
                d = self._array_data[index.row()]['validFrom']
                return d.strftime(self.date_format) if d is not None else ''
            elif index.column() == 5:
                d = self._array_data[index.row()]['validTo']
                return d.strftime(self.date_format) if d is not None else ''
        elif role == Qt.FontRole:
            if self.default_graph_version_index >= 0 and index.row() == self.default_graph_version_index:
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
        elif role == Qt.EditRole:
            graph_version = self._array_data[index.row()]['version']
            if index.column() == 4:
                try:
                    new_datetime = datetime.strptime(value + '+0000', self.date_read_format)
                except ValueError as e:
                    return False
                if self._array_data[index.row()]['validFrom'] != new_datetime:
                    self._array_data[index.row()]['validFrom'] = new_datetime
                    self.update_graph_version_validity(graph_version, 'validFrom', value)
            if index.column() == 5:
                try:
                    new_datetime = datetime.strptime(value + '+0000', self.date_read_format)
                except ValueError as e:
                    return False
                if self._array_data[index.row()]['validTo'] != new_datetime:
                    self._array_data[index.row()]['validTo'] = new_datetime
                    self.update_graph_version_validity(graph_version, 'validTo', value)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        # elif index.column() == 0:
        #     return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        # elif index.column() == 1:
        #     return Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif index.column() == 4:
            return Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif index.column() == 5:
            return Qt.ItemIsEnabled | Qt.ItemIsEditable
        return QAbstractTableModel.flags(self, index) | Qt.NoItemFlags
