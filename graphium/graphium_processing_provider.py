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

import os
# PyQt5 imports
from PyQt5.QtGui import (QIcon)
# qgis imports
from qgis.core import (QgsProcessingProvider)
# plugin imports
from ..graphium.utilities.algorithm.mapmatcher_algorithm import (MapMatcherAlgorithm)
from ..graphium.utilities.algorithm.track_gpx2json_algorithm import (TrackGpx2JsonAlgorithm)
from ..graphium.utilities.algorithm.routing_algorithm import (RoutingAlgorithm)
from ..graphium.utilities.algorithm.points_to_trajectory_algorithm import (PointsToTrajectoryAlgorithm)
from ..graphium.graph_data.algorithm.add_segment_geometry_algorithm import (AddSegmentGeometryAlgorithm)
from ..graphium.graph_data.algorithm.download_graph_version_algorithm import (DownloadGraphVersionAlgorithm)
from ..graphium.graph_data.algorithm.update_segment_attribute_algorithm import (UpdateSegmentAttributeAlgorithm)
from ..graphium.graph_data.algorithm.update_segment_geometry_algorithm import (UpdateSegmentGeometryAlgorithm)
from ..graphium.graph_management.algorithm.update_graph_version_attribute_algorithm import\
    (UpdateGraphVersionAttributeAlgorithm)
from ..graphium.graph_management.algorithm.update_graph_version_validity_algorithm import (
    UpdateGraphVersionValidityAlgorithm)
from ..graphium.graph_management.algorithm.add_graph_version_algorithm import (AddGraphVersionAlgorithm)
from ..graphium.graph_management.algorithm.activate_graph_version_algorithm import (ActivateGraphVersionAlgorithm)
from ..graphium.graph_management.algorithm.remove_graph_version_algorithm import (RemoveGraphVersionAlgorithm)
from ..graphium.graph_management.algorithm.set_default_graph_version_algorithm import (SetDefaultGraphVersionAlgorithm)
from ..graphium.graph_management.algorithm.gip2graphium_algorithm import (Gip2GraphiumAlgorithm)
from ..graphium.graph_management.algorithm.osm2graphium_algorithm import (Osm2GraphiumAlgorithm)


class GraphiumProcessingProvider(QgsProcessingProvider):

    # MY_DUMMY_SETTING = 'MY_DUMMY_SETTING'

    def __init__(self):
        super().__init__()

    def id(self):
        return "Graphium"

    def name(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'Graphium'

    def icon(self):
        """ We return the icon. """
        plugin_path = os.path.split(os.path.dirname(__file__))[0]

        return QIcon(os.path.join(plugin_path, 'icons/icon.svg'))
        # return QgsProcessingProvider.icon(self)

    # def initializeSettings(self):
    #     """In this method we add settings needed to configure our
    #     provider.
    #
    #     Do not forget to call the parent method, since it takes care
    #     or automatically adding a setting for activating or
    #     deactivating the algorithms in the provider.
    #     """
    #     QgsProcessingProvider.initializeSettings(self)
    #     # ProcessingConfig.addSetting(Setting('Example algorithms',
    #     #                                     GpxSegmentImporterProvider.MY_DUMMY_SETTING,
    #     #                                     'Example setting', 'Default value'))

    def load(self):
        """In this method we add settings needed to configure our provider."""
        # ProcessingConfig.settingIcons[self.name()] = self.icon()
        # # Deactivate provider by default
        # ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_EXAMPLE',
        #                                     'Activate', False))
        # ProcessingConfig.addSetting(Setting('Example algorithms',
        #                                     GpxSegmentImporterProvider.MY_DUMMY_SETTING,
        #                                     'Example setting', 'Default value'))
        # ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        # ProcessingConfig.removeSetting('ACTIVATE_EXAMPLE')
        # ProcessingConfig.removeSetting(GpxSegmentImporterProvider.MY_DUMMY_SETTING)

    def loadAlgorithms(self):
        """ This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.
        """
        self.addAlgorithm(MapMatcherAlgorithm())
        self.addAlgorithm(TrackGpx2JsonAlgorithm())
        self.addAlgorithm(RoutingAlgorithm())
        self.addAlgorithm(PointsToTrajectoryAlgorithm())
        self.addAlgorithm(AddSegmentGeometryAlgorithm())
        self.addAlgorithm(UpdateSegmentGeometryAlgorithm())
        self.addAlgorithm(DownloadGraphVersionAlgorithm())
        self.addAlgorithm(UpdateGraphVersionAttributeAlgorithm())
        self.addAlgorithm(AddGraphVersionAlgorithm())
        self.addAlgorithm(ActivateGraphVersionAlgorithm())
        self.addAlgorithm(RemoveGraphVersionAlgorithm())
        self.addAlgorithm(SetDefaultGraphVersionAlgorithm())
        self.addAlgorithm(Gip2GraphiumAlgorithm())
        self.addAlgorithm(Osm2GraphiumAlgorithm())
        self.addAlgorithm(UpdateSegmentAttributeAlgorithm())
        self.addAlgorithm(UpdateGraphVersionValidityAlgorithm())
