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

from enum import Enum


class FunctionalRoadClass(Enum):
    NOT_APPLICABLE = -1
    MOTORWAY_FREEWAY_OR_OTHER_MAJOR_MOTORWAY = 0
    MAJOR_ROAD_LESS_IMORTANT_THAN_MOTORWAY = 1
    OTHER_MAJOR_ROAD = 2
    SECONDARY_ROAD = 3
    LOCAL_CONNECTING_ROAD = 4
    LOCAL_ROAD_OF_HIGH_IMPORTANCE = 5
    LOCAL_ROAD = 6
    LOCAL_ROAD_OF_MINOR_IMPORTANCE = 7
    SONSTIGE_STRASSEN = 8
    RAD_FUSSWEG = 10
    WIRTSCHAFTSWEG = 11
    FERNVERKEHRSGLEIS = 20
    STRASSENBAHNGLEIS = 24
    U_BAHN_GLEIS = 25
    FAEHRE = 31
    TREPPE = 45
    ROLLTREPPE = 46
    AUFZUG = 47
    RAMPE = 48
    FUSSWEG_OHNE_ANZEIGE = 101
    FUSSWEGPASSAGE = 102
    SEILBAHN_UND_SONSTIGE = 103
    SONDERELEMENT = 104
    ALMAUFSCHLIESSUNGSWEG = 105
    FORSTAUFSCHLIESSUNGSWEG = 106
    HOFZUFAHRTEN = 107
    GUETERWEG = 108
