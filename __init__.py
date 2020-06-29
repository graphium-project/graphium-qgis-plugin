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
# This script initializes the plugin, making it known to QGIS.

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GraphiumQGIS class from file GraphiumQGIS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .graphium_qgis import GraphiumQGIS
    return GraphiumQGIS(iface)
