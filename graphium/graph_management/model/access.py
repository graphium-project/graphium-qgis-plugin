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


class Access(Enum):
    PEDESTRIAN = 1
    BIKE = 2
    PRIVATE_CAR = 3
    PUBLIC_BUS = 4
    RAILWAY = 5
    TRAM = 6
    SUBWAY = 7
    FERRY_BOAT = 8
    HIGH_OCCUPATION_CAR = 9
    TRUCK = 10
    TAXI = 11
    EMERGENCY_VEHICLE = 12
    MOTOR_COACH = 13
    TROLLY_BUS = 14
    MOTORCYCLE = 15
    RACK_RAILWAY = 16
    CABLE_RAILWAY = 17
    CAR_FERRY = 18
    CAMPER = 19
    COMBUSTIBLES = 20
    HAZARDOUS_TO_WATER = 21
    GARBAGE_COLLECTION_VEHICLE = 22
    ELECTRIC_CAR = 23
    NONE = -1
