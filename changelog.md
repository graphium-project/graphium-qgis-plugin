v1.2 (2021-12-21)
   * [Feature] [manager] Added graph name task menu button
   * [Feature] [manager] Added graph version task menu button
   * [Feature] [utility] New algorithm TrajectoryToPoints Converter
   * [Feature] [utility] New parameter routing_mode in mapmatching algorithm
   * [Feature] [utility] optionally add header attributes in trajectoryToPoints alg
   * [Feature] [graph data] Automatically detect graph type at downloadGraphVersion alg
   * [Feature] [graph data] add geometry as attribute option to update segment attribute algorithm
   * [Feature] Add graph select dialog, which can be used in sub-plugins
   * [Feature] Add qgis hd segment style files in qgis directory
   * [Improvement] [manager] Activate graph version moved to task menu button
   * [Improvement] [manager] Delete graph version moved to task menu button
   * [Improvement] [graph_data] Friendly error message if input file is missing at graph import
   * [Improvement] [graph_data] Faster AddSegmentGeometry algorithm as batches are created instead of single requests
   * [Improvement] [graph data] do not log missing geometry at add segment geometry alg in order to reduce logging
   * [Improvement] [graph data] modify updateSegmentAttribute alg to non-feature-based alg
   * [Improvement] [graph data] create JSON lists for access attr in download graph version alg
   * [Improvement] [utility] Correctly calculate track duration in gpx2json algorithm
   * [Improvement] [utility] Add track point id to JSON output of PointsToTrajectory algorithm
   * [Improvement] [utility] check if timestamp and geometry are available in PointsToTrajectory alg
   * [Improvement] [utility] only add z if 3d in PointsToTrajectory algorithm
   * [Improvement] [utility] set gpx2json in map-matcher alg als child algorithm
   * [Improvement] [gip2graphium] Do not add frc and access arguments if all options are selected
   * [Improvement] [connection] Mention create or edit action in dialog header
   * [Improvement] [http-rest-api] Optionally do not write url to feedback
   * [Improvement] [http-rest-api] add timeout parameter to get requests
   * [Fixed] Do not use fileFilter at initializing QgsProcessingParameterFile temporarily
   * [Fixed] [http rest api] Only use setTransferTimeout for request if function is available
   * [Deprecated] Setting hd_enabled deprecated

v1.1 (2021-03-23)

 * [Feature] Read-only flag for Graphium connections
 * [Feature] Double click table to download graph version in manager
 * [Feature] Include algorithm pointsToTrajectory
 * [Feature] Add connection json string as attribute to output layer in download_graph_version_algorithm
 * [Feature] Enable adding and removing hd graph versions (optional feature)
 * [Feature] Enable downloading hd graph data (optional feature)
 * [Feature] Set authentication for server connection (optional feature)
 * [Improvement] Read metadata to detect graph type in add_graph_version_algorithm
 * [Improvement] Save output direction in qgis settings in osm2graphium and gip2graphium
 * [Improvement] Disable buttons that cannot be used before selecting graph name or version
 * [Improvement] Sort connections in combo box by name in manager
 * [Improvement] Double click to select graph name or download graph version in manager
 * [Improvement] Add status code to error feedback in api
 * [Fixed] Correct progress value in download_graph_version_algorithm
 * [Fixed] long datatype for id/startNodeId/endNodeId in  download_graph_version_algorithm
 * [Fixed] long datatype for segmentId in  download_graph_version_algorithm
 * [Fixed] Remove unreliable segment count check in download_graph_version_algorithm 

v1.0 (2020-07-08)

 * [Feature] New algorithm UpdateGraphVersionValidity
 * [Feature] Add valid_from and valid_to parameters to gip2graphium  and osm2graphium algorithms
 * [Improvement] Menu button to launch all AddGraphVersion algorithms (add/gip/osm) in manager
 * [Improvement] Add request type to url in feedback in api
 * [Improvement] QgsNetworkAccessManager, timeout and downloadProgress for all requests (including PUT/DELETE) in api
 * [Improvement] Simplify output of remove_graph_version_algorithm to state only
 * [Improvement] Graphium icons for all algorithms
 * [Improvement] Use checkParameterValues to check new date in UpdateGraphVersionValidityAlgorithm
 * [Fixed] Provide useful error feedback at AddGraphVersion algorithm
 * [Fixed] Better message in case of decode error at osm2graphium/gip2graphium
 * [Fixed] Allow aborting GET and POST requests
 * [Fixed] Select correct server at gip2graphium algorithm if set via parameter
 * [Fixed] Never use processing.QgisAlgorithm to improve stability
 * [Fixed] Disable unused keepDownloadFile and forceDownload parameters in gip2graphium and osm2graphium algorithms

v0.7 (2020-07-01)

 * [Feature] Add refresh buttons for graph name and version tables
 * [Improvement] Mention selected server above graph name table
 * [Improvement] Disable graph management group until successfully connecting to server in manager
 * [Improvement] Graph name/version set as default is displayed with bold font in table in manager
 * [Fixed] Show number of graph versions for each graph name without delay in manager
 * [Fixed] Clear graph name table if connecting to server fails in manager
 * [Fixed] Do not automatically add /api to url
 * Temporarily hide is_hd_segments parameter at add graph version algorithm

v0.6 (2020-06-29)

 * [Feature] License changed to Apache 2.0
 * [Fixed] Unused geomtools removed
 * Change Detection Features (Detect Changes Algorithm and Change Set Dialog) temporarily removed

v0.5 (2020-06-29)

 * [Feature] Add algorithm UpdateSegmentAttribute
 * [Feature] Add overrideIfExists parameter in gip2graphium/osm2graphium algorithms
 * [Feature] Additionally save JSON output at DownloadGraphVersion algorithm
 * [Fixed] Fix parsing timeout_sec if it is not set
 * [Fixed] Do not allow storing output of gip2graphium/osm2graphium algs in temporary folders
 * [Fixed] Clear old content in graph name table if connected server does not have any graph names
 * [Fixed] Clear old content in graph version table if connected graph name does not have any versions
 
 v0.4 (2020-06-24)
 
 * [Feature] Add QGIS setting timeout_sec to handle timeout in api (default=10min)
 * [Feature] Add parameter keep_metadata to remove graph version algorithm
 * [Feature] Filter graph versions in manager by state (inital/active/deleted)
 * [Feature] Number of graph versions listed for every graph name in manager
 * [Improvement] Graph server drop down for all graph management and graph data algorithms
 * [Improvement] Launch osm2graphium and gip2graphium algorithms from menu
 * [Improvement] Pixel cut parameters at gip2graphium algorithm removed
 * [Fixed] Parsing timestamps with format %Y-%m-%dT%H:%M:%SZ in gpx2json algorithm
 * [Fixed] Parse all track segments in gpx2json algorithm
 * [Fixed] Sorting graph names (alphabetically) and versions (valid_from)
 * [Fixed] Fix output of state at add graph version algorithm
 * [Fixed] Useful error messages if graph version has been deleted at graph data algorithms
 * [Fixed] Useful error message if empty response from api
 
 v0.3 (2020-06-23)
 
 * [Feature] Added algorithm Osm2Graphium
 * [Improvement] Separated views for graph name and graph version in manager
 * [Improvement] Graph names listed in table instead of drop down box in manager
 * [Improvement] Algorithm Gip2Graphium extended with new parameters
 * [Improvement] Selectable lists for frc and access selection at Gip2Graphium algorithm
 * [Improvement] Simplified connection editor
 * [Improvement] Select graph server with a drop down at mapmatching, routing, gip2graphium and osm2graphium algorithms
 * [Improvement] Use api/capabilities call to check mapmatching and routing capability
 * [Improvement] Change detection dialog stays on top of the QGIS main windows
 
v0.2 (2020-06-12)
 
 * [Fixed|Breaking] Automatic '/api' extension for PostgreSQL-connection base urls removed
 * [Feature] Added algorithm Gip2Graphium
 * [Feature] Added algorithm SetDefaultGraphVersion
 * [Feature] Short help texts for all algorithms
 * [Improvement] Graph manager dialog stays on top of the QGIS main windows
 * [Improvement] http://localhost as default connection url (instead of http://example.at)
 * [Improvement] graphium/api as default base url (instead of graphium)
 * [Improvement] Add 'Download' button to graph manager
 * [Improvement] Make default graph server/name/version labels selectable in graph manager
 * [Fixed] Empty attribute accessTow in DownloadGraphVersion algorithm
 
 v0.1 (2020-06-03)
 
 * Initial preview release