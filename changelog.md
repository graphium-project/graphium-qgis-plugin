v0.6 (2020-06-29)

 * License change to Apache 2.0

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