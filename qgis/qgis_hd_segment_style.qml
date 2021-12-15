<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="0" styleCategories="Symbology|Labeling" version="3.22.1-Białowieża">
  <renderer-v2 referencescale="-1" enableorderby="0" type="singleSymbol" forceraster="0" symbollevels="0">
    <symbols>
      <symbol clip_to_extent="1" type="line" name="0" force_rhr="0" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" pass="0" class="GeometryGenerator" locked="0">
          <Option type="Map">
            <Option value="Fill" type="QString" name="SymbolType"/>
            <Option value="make_polygon( line_merge(collect_geometries(&#xd;&#xa;CASE&#xd;&#xa;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = True&#xd;&#xa;&#x9;AND map_get( from_json( &quot;tags&quot; ), 'invertedBorder') IN ('both', 'left')&#xd;&#xa;THEN reverse( geom_from_wkt( &quot;leftBorderGeometry&quot;))&#xd;&#xa;ELSE geom_from_wkt(&quot;leftBorderGeometry&quot;)&#xd;&#xa;END,&#xd;&#xa;&#xd;&#xa;make_line(&#xd;&#xa;&#x9;&#xd;&#xa;&#x9; point_n(geom_from_wkt(&quot;leftBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT IN ('both', 'left')&#xd;&#xa;&#x9;&#x9;THEN -1 ELSE 1 END),&#xd;&#xa;&#x9;point_n(geom_from_wkt(&quot;rightBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'right')&#xd;&#xa;&#x9;&#x9;THEN -1 ELSE 1 END)&#xd;&#xa;),&#xd;&#xa;&#xd;&#xa;CASE&#xd;&#xa;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = True&#xd;&#xa; &#x9;AND map_get( from_json( &quot;tags&quot; ), 'invertedBorder') IN ('both', 'right')&#xd;&#xa;THEN geom_from_wkt( &quot;rightBorderGeometry&quot;)&#xd;&#xa;ELSE reverse( geom_from_wkt(&quot;rightBorderGeometry&quot;))&#xd;&#xa;END,&#xd;&#xa;&#xd;&#xa;make_line(&#xd;&#xa;&#x9;&#xd;&#xa;&#x9; point_n(geom_from_wkt(&quot;rightBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'right')&#xd;&#xa;&#x9;&#x9;THEN 1 ELSE -1 END),&#xd;&#xa;&#x9;point_n(geom_from_wkt(&quot;leftBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'left')&#xd;&#xa;&#x9;&#x9;THEN 1 ELSE -1 END)&#xd;&#xa;)&#xd;&#xa;&#xd;&#xa;)))&#xd;&#xa;" type="QString" name="geometryModifier"/>
            <Option value="MapUnit" type="QString" name="units"/>
          </Option>
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="make_polygon( line_merge(collect_geometries(&#xd;&#xa;CASE&#xd;&#xa;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = True&#xd;&#xa;&#x9;AND map_get( from_json( &quot;tags&quot; ), 'invertedBorder') IN ('both', 'left')&#xd;&#xa;THEN reverse( geom_from_wkt( &quot;leftBorderGeometry&quot;))&#xd;&#xa;ELSE geom_from_wkt(&quot;leftBorderGeometry&quot;)&#xd;&#xa;END,&#xd;&#xa;&#xd;&#xa;make_line(&#xd;&#xa;&#x9;&#xd;&#xa;&#x9; point_n(geom_from_wkt(&quot;leftBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT IN ('both', 'left')&#xd;&#xa;&#x9;&#x9;THEN -1 ELSE 1 END),&#xd;&#xa;&#x9;point_n(geom_from_wkt(&quot;rightBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'right')&#xd;&#xa;&#x9;&#x9;THEN -1 ELSE 1 END)&#xd;&#xa;),&#xd;&#xa;&#xd;&#xa;CASE&#xd;&#xa;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = True&#xd;&#xa; &#x9;AND map_get( from_json( &quot;tags&quot; ), 'invertedBorder') IN ('both', 'right')&#xd;&#xa;THEN geom_from_wkt( &quot;rightBorderGeometry&quot;)&#xd;&#xa;ELSE reverse( geom_from_wkt(&quot;rightBorderGeometry&quot;))&#xd;&#xa;END,&#xd;&#xa;&#xd;&#xa;make_line(&#xd;&#xa;&#x9;&#xd;&#xa;&#x9; point_n(geom_from_wkt(&quot;rightBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'right')&#xd;&#xa;&#x9;&#x9;THEN 1 ELSE -1 END),&#xd;&#xa;&#x9;point_n(geom_from_wkt(&quot;leftBorderGeometry&quot;),&#xd;&#xa;&#x9;&#x9;CASE&#xd;&#xa;&#x9;&#x9;WHEN map_exist(from_json( &quot;tags&quot; ), 'invertedBorder') = False&#xd;&#xa;&#x9;&#x9;OR map_get( from_json( &quot;tags&quot; ), 'invertedBorder') NOT  IN ('both', 'left')&#xd;&#xa;&#x9;&#x9;THEN 1 ELSE -1 END)&#xd;&#xa;)&#xd;&#xa;&#xd;&#xa;)))&#xd;&#xa;"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="enabled">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="@map_scale &lt; 5000" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" type="fill" name="@0@0" force_rhr="0" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" pass="0" class="SimpleFill" locked="0">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="174,235,255,255" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="174,235,255,255" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0.2" type="QString" name="outline_width"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="174,235,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="174,235,255,255"/>
              <prop k="outline_style" v="no"/>
              <prop k="outline_width" v="0.2"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="fillColor">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="lighter( coalesce(project_color(map_get(from_json( &quot;tags&quot; ), 'roadType')) ,project_color( 'default'), '#666666'), 124)" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                    <Option type="Map" name="outlineColor">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="darker(coalesce(project_color(map_get(from_json( &quot;tags&quot; ), 'roadType')) ,project_color( 'default'), '#666666'), 124)" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" pass="0" class="SimpleLine" locked="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="0.5;1" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="219,219,219,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.26" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="1" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="square"/>
          <prop k="customdash" v="0.5;1"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="line_color" v="219,219,219,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.26"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="1"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="enabled">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="@map_scale &lt; 1000" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
                <Option type="Map" name="outlineColor">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="@symbol_color" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer enabled="1" pass="0" class="MarkerLine" locked="0">
          <Option type="Map">
            <Option value="4" type="QString" name="average_angle_length"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
            <Option value="MM" type="QString" name="average_angle_unit"/>
            <Option value="10" type="QString" name="interval"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
            <Option value="MM" type="QString" name="interval_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="0" type="QString" name="offset_along_line"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_along_line_unit"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="interval" type="QString" name="placement"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="1" type="QString" name="rotate"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="10"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="interval"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="enabled">
                  <Option value="true" type="bool" name="active"/>
                  <Option value="@map_scale &lt; 1000&#xd;&#xa;AND&#xd;&#xa;array_contains(string_to_array(  &quot;accessTow&quot; ), 'PRIVATE_CAR')" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" type="marker" name="@0@2" force_rhr="0" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" pass="0" class="SimpleMarker" locked="0">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="255,0,0,255" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="arrowhead" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="1.2" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="MM" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1.2"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="outlineColor">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="coalesce(project_color(map_get(from_json( &quot;tags&quot; ), 'roadType')) ,project_color( 'default'), '#666666')" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" pass="0" class="GeometryGenerator" locked="0">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="geom_from_wkt(&quot;leftBorderGeometry&quot; )" type="QString" name="geometryModifier"/>
            <Option value="MapUnit" type="QString" name="units"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt(&quot;leftBorderGeometry&quot; )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="enabled">
                  <Option value="false" type="bool" name="active"/>
                  <Option value="@map_scale &lt; 2000" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" type="line" name="@0@3" force_rhr="0" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" pass="0" class="SimpleLine" locked="0">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="MM" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="174,235,255,255" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="0.26" type="QString" name="line_width"/>
                <Option value="MM" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="174,235,255,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.26"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="outlineColor">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="coalesce(project_color(map_get(from_json( &quot;tags&quot; ), 'roadType')) ,project_color( 'default'), '#666666')" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer enabled="1" pass="0" class="MarkerLine" locked="0">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="MM" type="QString" name="average_angle_unit"/>
                <Option value="10" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="MM" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="interval" type="QString" name="placement"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="10"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="interval"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="enabled">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="@map_scale &lt; 500" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol clip_to_extent="1" type="marker" name="@@0@3@1" force_rhr="0" alpha="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" pass="0" class="SimpleMarker" locked="0">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="255,0,0,255" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="arrowhead" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="174,235,255,255" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="1.2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="cap_style" v="square"/>
                  <prop k="color" v="255,0,0,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="arrowhead"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="174,235,255,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="1.2"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option type="Map" name="properties">
                        <Option type="Map" name="outlineColor">
                          <Option value="true" type="bool" name="active"/>
                          <Option value="@symbol_color" type="QString" name="expression"/>
                          <Option value="3" type="int" name="type"/>
                        </Option>
                      </Option>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" pass="0" class="GeometryGenerator" locked="0">
          <Option type="Map">
            <Option value="Line" type="QString" name="SymbolType"/>
            <Option value="geom_from_wkt(&quot;rightBorderGeometry&quot;)" type="QString" name="geometryModifier"/>
            <Option value="MapUnit" type="QString" name="units"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="geom_from_wkt(&quot;rightBorderGeometry&quot;)"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="enabled">
                  <Option value="false" type="bool" name="active"/>
                  <Option value="@map_scale &lt; 2000" type="QString" name="expression"/>
                  <Option value="3" type="int" name="type"/>
                </Option>
              </Option>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" type="line" name="@0@4" force_rhr="0" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" pass="0" class="SimpleLine" locked="0">
              <Option type="Map">
                <Option value="0" type="QString" name="align_dash_pattern"/>
                <Option value="square" type="QString" name="capstyle"/>
                <Option value="5;2" type="QString" name="customdash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
                <Option value="MM" type="QString" name="customdash_unit"/>
                <Option value="0" type="QString" name="dash_pattern_offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
                <Option value="0" type="QString" name="draw_inside_polygon"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="174,235,255,255" type="QString" name="line_color"/>
                <Option value="solid" type="QString" name="line_style"/>
                <Option value="0.26" type="QString" name="line_width"/>
                <Option value="MM" type="QString" name="line_width_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="0" type="QString" name="trim_distance_end"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_end_unit"/>
                <Option value="0" type="QString" name="trim_distance_start"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
                <Option value="MM" type="QString" name="trim_distance_start_unit"/>
                <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
                <Option value="0" type="QString" name="use_custom_dash"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="174,235,255,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.26"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="outlineColor">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="coalesce(project_color(map_get(from_json( &quot;tags&quot; ), 'roadType')) ,project_color( 'default'), '#666666')" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer enabled="1" pass="0" class="MarkerLine" locked="0">
              <Option type="Map">
                <Option value="4" type="QString" name="average_angle_length"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="average_angle_map_unit_scale"/>
                <Option value="MM" type="QString" name="average_angle_unit"/>
                <Option value="10" type="QString" name="interval"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="interval_map_unit_scale"/>
                <Option value="MM" type="QString" name="interval_unit"/>
                <Option value="0" type="QString" name="offset"/>
                <Option value="0" type="QString" name="offset_along_line"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_along_line_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_along_line_unit"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="interval" type="QString" name="placement"/>
                <Option value="0" type="QString" name="ring_filter"/>
                <Option value="1" type="QString" name="rotate"/>
              </Option>
              <prop k="average_angle_length" v="4"/>
              <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="average_angle_unit" v="MM"/>
              <prop k="interval" v="10"/>
              <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="interval_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_along_line" v="0"/>
              <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_along_line_unit" v="MM"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="placement" v="interval"/>
              <prop k="ring_filter" v="0"/>
              <prop k="rotate" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option type="Map" name="properties">
                    <Option type="Map" name="enabled">
                      <Option value="true" type="bool" name="active"/>
                      <Option value="@map_scale &lt; 500" type="QString" name="expression"/>
                      <Option value="3" type="int" name="type"/>
                    </Option>
                  </Option>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
              <symbol clip_to_extent="1" type="marker" name="@@0@4@1" force_rhr="0" alpha="1">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" type="QString" name="name"/>
                    <Option name="properties"/>
                    <Option value="collection" type="QString" name="type"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" pass="0" class="SimpleMarker" locked="0">
                  <Option type="Map">
                    <Option value="0" type="QString" name="angle"/>
                    <Option value="square" type="QString" name="cap_style"/>
                    <Option value="255,0,0,255" type="QString" name="color"/>
                    <Option value="1" type="QString" name="horizontal_anchor_point"/>
                    <Option value="bevel" type="QString" name="joinstyle"/>
                    <Option value="arrowhead" type="QString" name="name"/>
                    <Option value="0,0" type="QString" name="offset"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                    <Option value="MM" type="QString" name="offset_unit"/>
                    <Option value="174,235,255,255" type="QString" name="outline_color"/>
                    <Option value="solid" type="QString" name="outline_style"/>
                    <Option value="0" type="QString" name="outline_width"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                    <Option value="MM" type="QString" name="outline_width_unit"/>
                    <Option value="diameter" type="QString" name="scale_method"/>
                    <Option value="1.2" type="QString" name="size"/>
                    <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                    <Option value="MM" type="QString" name="size_unit"/>
                    <Option value="1" type="QString" name="vertical_anchor_point"/>
                  </Option>
                  <prop k="angle" v="0"/>
                  <prop k="cap_style" v="square"/>
                  <prop k="color" v="255,0,0,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="arrowhead"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="174,235,255,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="1.2"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" type="QString" name="name"/>
                      <Option type="Map" name="properties">
                        <Option type="Map" name="outlineColor">
                          <Option value="true" type="bool" name="active"/>
                          <Option value="@symbol_color" type="QString" name="expression"/>
                          <Option value="3" type="int" name="type"/>
                        </Option>
                      </Option>
                      <Option value="collection" type="QString" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>6</featureBlendMode>
  <layerGeometryType>1</layerGeometryType>
</qgis>
