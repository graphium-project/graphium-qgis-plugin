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