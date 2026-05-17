<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="1" version="3.16.1-Hannover" simplifyMaxScale="1" simplifyDrawingHints="0" labelsEnabled="1" styleCategories="AllStyleCategories" minScale="100000000" simplifyDrawingTol="1" simplifyAlgorithm="0" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal accumulate="0" startField="" durationUnit="min" startExpression="" endExpression="" enabled="0" mode="0" fixedDuration="0" endField="" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 forceraster="0" type="singleSymbol" enableorderby="0" symbollevels="0">
    <symbols>
      <symbol force_rhr="0" type="fill" name="0" clip_to_extent="1" alpha="1">
        <layer class="ShapeburstFill" enabled="1" locked="0" pass="0">
          <prop v="10" k="blur_radius"/>
          <prop v="255,127,0,255" k="color"/>
          <prop v="0,0,255,255" k="color1"/>
          <prop v="0,255,0,255" k="color2"/>
          <prop v="0" k="color_type"/>
          <prop v="0" k="discrete"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="Pixel" k="distance_unit"/>
          <prop v="255,127,0,0" k="gradient_color2"/>
          <prop v="1" k="ignore_rings"/>
          <prop v="1" k="max_distance"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="gradient" k="rampType"/>
          <prop v="0" k="use_whole_shape"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleFill" enabled="1" locked="0" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,127,0,26" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,127,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.75" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
    <effect type="effectStack" enabled="0">
      <effect type="dropShadow">
        <prop v="13" k="blend_mode"/>
        <prop v="0.7935" k="blur_level"/>
        <prop v="MM" k="blur_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
        <prop v="0,0,0,255" k="color"/>
        <prop v="2" k="draw_mode"/>
        <prop v="1" k="enabled"/>
        <prop v="135" k="offset_angle"/>
        <prop v="0.5" k="offset_distance"/>
        <prop v="MM" k="offset_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
        <prop v="0.7" k="opacity"/>
      </effect>
      <effect type="outerGlow">
        <prop v="0" k="blend_mode"/>
        <prop v="0.7935" k="blur_level"/>
        <prop v="MM" k="blur_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
        <prop v="0,0,255,255" k="color1"/>
        <prop v="0,255,0,255" k="color2"/>
        <prop v="0" k="color_type"/>
        <prop v="0" k="discrete"/>
        <prop v="2" k="draw_mode"/>
        <prop v="0" k="enabled"/>
        <prop v="0.5" k="opacity"/>
        <prop v="gradient" k="rampType"/>
        <prop v="255,255,255,255" k="single_color"/>
        <prop v="2" k="spread"/>
        <prop v="MM" k="spread_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
      </effect>
      <effect type="drawSource">
        <prop v="0" k="blend_mode"/>
        <prop v="2" k="draw_mode"/>
        <prop v="1" k="enabled"/>
        <prop v="1" k="opacity"/>
      </effect>
      <effect type="innerShadow">
        <prop v="13" k="blend_mode"/>
        <prop v="2.645" k="blur_level"/>
        <prop v="MM" k="blur_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
        <prop v="0,0,0,255" k="color"/>
        <prop v="2" k="draw_mode"/>
        <prop v="0" k="enabled"/>
        <prop v="135" k="offset_angle"/>
        <prop v="2" k="offset_distance"/>
        <prop v="MM" k="offset_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
        <prop v="1" k="opacity"/>
      </effect>
      <effect type="innerGlow">
        <prop v="0" k="blend_mode"/>
        <prop v="0.7935" k="blur_level"/>
        <prop v="MM" k="blur_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
        <prop v="0,0,255,255" k="color1"/>
        <prop v="0,255,0,255" k="color2"/>
        <prop v="0" k="color_type"/>
        <prop v="0" k="discrete"/>
        <prop v="2" k="draw_mode"/>
        <prop v="0" k="enabled"/>
        <prop v="0.5" k="opacity"/>
        <prop v="gradient" k="rampType"/>
        <prop v="255,255,255,255" k="single_color"/>
        <prop v="2" k="spread"/>
        <prop v="MM" k="spread_unit"/>
        <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
      </effect>
    </effect>
  </renderer-v2>
  <labeling type="rule-based">
    <rules key="{303b3fac-1c10-48cf-b5a3-e78fc02ebc15}">
      <rule key="{ebef04f2-f6dd-456d-97a7-e6e055781f0c}" description="Out">
        <settings calloutType="simple">
          <text-style fontSizeUnit="Point" allowHtml="0" fontUnderline="0" blendMode="0" fontWordSpacing="0" fontLetterSpacing="0" textColor="0,0,0,255" fontWeight="50" fontItalic="0" fieldName="'ASMA ' + to_string(&quot;ASMA_No&quot; )" fontStrikeout="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" fontFamily="Calibri" previewBkgrdColor="255,255,255,255" capitalization="0" textOpacity="1" namedStyle="Normal" fontSize="10" multilineHeight="1" isExpression="1" fontKerning="1" textOrientation="horizontal">
            <text-buffer bufferSize="1" bufferSizeUnits="MM" bufferNoFill="0" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferBlendMode="0" bufferDraw="1" bufferColor="255,242,229,255"/>
            <text-mask maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskedSymbolLayers="" maskSizeUnits="MM" maskSize="0"/>
            <background shapeDraw="0" shapeRadiiUnit="MM" shapeSizeUnit="MM" shapeRotation="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderColor="128,128,128,255" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeRadiiX="0" shapeBorderWidth="0" shapeOffsetX="0" shapeJoinStyle="64" shapeSVGFile="" shapeSizeX="0" shapeRotationType="0" shapeFillColor="255,255,255,255" shapeOffsetUnit="MM" shapeBorderWidthUnit="MM" shapeOffsetY="0" shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <shadow shadowRadius="1.5" shadowOpacity="0.7" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetDist="1" shadowColor="0,0,0,255" shadowOffsetUnit="MM" shadowDraw="1" shadowUnder="0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowBlendMode="6" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format plussign="0" multilineAlign="4294967295" decimals="3" useMaxLineLengthForAutoWrap="1" autoWrapLength="0" addDirectionSymbol="0" rightDirectionSymbol=">" placeDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" reverseDirectionSymbol="0" formatNumbers="0"/>
          <placement distUnits="MM" offsetType="0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="UnknownGeometry" repeatDistance="0" lineAnchorPercent="0.5" quadOffset="4" dist="0" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MapUnit" placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="" centroidWhole="0" xOffset="0" preserveRotation="1" geometryGeneratorType="PointGeometry" overrunDistanceUnit="MM" yOffset="0" maxCurvedCharAngleIn="25" overrunDistance="0" lineAnchorType="0" fitInPolygonOnly="0" geometryGeneratorEnabled="0" maxCurvedCharAngleOut="-25" repeatDistanceUnits="MM" polygonPlacementFlags="2" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" priority="5"/>
          <rendering obstacleFactor="1" scaleMax="5000001" maxNumLabels="2000" obstacleType="0" labelPerPart="0" obstacle="1" mergeLines="0" fontLimitPixelSize="0" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" zIndex="0" scaleVisibility="1" fontMaxPixelSize="10000" displayAll="1" scaleMin="1000001" limitNumLabels="0" fontMinPixelSize="3"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol force_rhr=&quot;0&quot; type=&quot;line&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule key="{791e9556-df8b-4728-84e4-7d2b64a698d3}" description="In">
        <settings calloutType="simple">
          <text-style fontSizeUnit="Point" allowHtml="0" fontUnderline="0" blendMode="0" fontWordSpacing="0" fontLetterSpacing="0" textColor="0,0,0,255" fontWeight="50" fontItalic="0" fieldName="'ASMA ' + to_string(&quot;ASMA_No&quot; ) + ': ' +  &quot;Name&quot; " fontStrikeout="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" fontFamily="Calibri" previewBkgrdColor="255,255,255,255" capitalization="0" textOpacity="1" namedStyle="Normal" fontSize="10" multilineHeight="1" isExpression="1" fontKerning="1" textOrientation="horizontal">
            <text-buffer bufferSize="1" bufferSizeUnits="MM" bufferNoFill="0" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferBlendMode="0" bufferDraw="1" bufferColor="255,242,229,255"/>
            <text-mask maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskedSymbolLayers="" maskSizeUnits="MM" maskSize="0"/>
            <background shapeDraw="0" shapeRadiiUnit="MM" shapeSizeUnit="MM" shapeRotation="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderColor="128,128,128,255" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeRadiiX="0" shapeBorderWidth="0" shapeOffsetX="0" shapeJoinStyle="64" shapeSVGFile="" shapeSizeX="0" shapeRotationType="0" shapeFillColor="255,255,255,255" shapeOffsetUnit="MM" shapeBorderWidthUnit="MM" shapeOffsetY="0" shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0"/>
            <shadow shadowRadius="1.5" shadowOpacity="0.7" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetDist="1" shadowColor="0,0,0,255" shadowOffsetUnit="MM" shadowDraw="1" shadowUnder="0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowBlendMode="6" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format plussign="0" multilineAlign="0" decimals="3" useMaxLineLengthForAutoWrap="1" autoWrapLength="0" addDirectionSymbol="0" rightDirectionSymbol=">" placeDirectionSymbol="0" leftDirectionSymbol="&lt;" wrapChar="" reverseDirectionSymbol="0" formatNumbers="0"/>
          <placement distUnits="MM" offsetType="0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="UnknownGeometry" repeatDistance="0" lineAnchorPercent="0.5" quadOffset="4" dist="0" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MapUnit" placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="" centroidWhole="0" xOffset="0" preserveRotation="1" geometryGeneratorType="PointGeometry" overrunDistanceUnit="MM" yOffset="0" maxCurvedCharAngleIn="25" overrunDistance="0" lineAnchorType="0" fitInPolygonOnly="0" geometryGeneratorEnabled="0" maxCurvedCharAngleOut="-25" repeatDistanceUnits="MM" polygonPlacementFlags="2" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" priority="5"/>
          <rendering obstacleFactor="1" scaleMax="1000001" maxNumLabels="2000" obstacleType="0" labelPerPart="0" obstacle="1" mergeLines="0" fontLimitPixelSize="0" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" zIndex="0" scaleVisibility="1" fontMaxPixelSize="10000" displayAll="1" scaleMin="1" limitNumLabels="0" fontMinPixelSize="3"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
              <Option type="Map" name="ddProperties">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
              <Option value="false" type="bool" name="drawToAllParts"/>
              <Option value="0" type="QString" name="enabled"/>
              <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
              <Option value="&lt;symbol force_rhr=&quot;0&quot; type=&quot;line&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
              <Option value="0" type="double" name="minLength"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
              <Option value="MM" type="QString" name="minLengthUnit"/>
              <Option value="0" type="double" name="offsetFromAnchor"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
              <Option value="0" type="double" name="offsetFromLabel"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
              <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property value="false" key="labeling/addDirectionSymbol"/>
    <property value="0" key="labeling/angleOffset"/>
    <property value="0" key="labeling/blendMode"/>
    <property value="0" key="labeling/bufferBlendMode"/>
    <property value="255" key="labeling/bufferColorA"/>
    <property value="255" key="labeling/bufferColorB"/>
    <property value="255" key="labeling/bufferColorG"/>
    <property value="255" key="labeling/bufferColorR"/>
    <property value="true" key="labeling/bufferDraw"/>
    <property value="128" key="labeling/bufferJoinStyle"/>
    <property value="false" key="labeling/bufferNoFill"/>
    <property value="0.9" key="labeling/bufferSize"/>
    <property value="false" key="labeling/bufferSizeInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/bufferSizeMapUnitScale"/>
    <property value="0" key="labeling/bufferTransp"/>
    <property value="false" key="labeling/centroidInside"/>
    <property value="false" key="labeling/centroidWhole"/>
    <property value="3" key="labeling/decimals"/>
    <property value="false" key="labeling/displayAll"/>
    <property value="0" key="labeling/dist"/>
    <property value="false" key="labeling/distInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/distMapUnitScale"/>
    <property value="true" key="labeling/drawLabels"/>
    <property value="true" key="labeling/enabled"/>
    <property value="Name || ' (ASMA No. '  ||  &quot;ASMA_No&quot;  || ')'" key="labeling/fieldName"/>
    <property value="false" key="labeling/fitInPolygonOnly"/>
    <property value="0" key="labeling/fontCapitals"/>
    <property value="Garamond" key="labeling/fontFamily"/>
    <property value="false" key="labeling/fontItalic"/>
    <property value="0" key="labeling/fontLetterSpacing"/>
    <property value="false" key="labeling/fontLimitPixelSize"/>
    <property value="100" key="labeling/fontMaxPixelSize"/>
    <property value="30" key="labeling/fontMinPixelSize"/>
    <property value="10" key="labeling/fontSize"/>
    <property value="false" key="labeling/fontSizeInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/fontSizeMapUnitScale"/>
    <property value="false" key="labeling/fontStrikeout"/>
    <property value="false" key="labeling/fontUnderline"/>
    <property value="75" key="labeling/fontWeight"/>
    <property value="0" key="labeling/fontWordSpacing"/>
    <property value="false" key="labeling/formatNumbers"/>
    <property value="true" key="labeling/isExpression"/>
    <property value="true" key="labeling/labelOffsetInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/labelOffsetMapUnitScale"/>
    <property value="false" key="labeling/labelPerPart"/>
    <property value="&lt;" key="labeling/leftDirectionSymbol"/>
    <property value="false" key="labeling/limitNumLabels"/>
    <property value="25" key="labeling/maxCurvedCharAngleIn"/>
    <property value="-25" key="labeling/maxCurvedCharAngleOut"/>
    <property value="2000" key="labeling/maxNumLabels"/>
    <property value="false" key="labeling/mergeLines"/>
    <property value="0" key="labeling/minFeatureSize"/>
    <property value="1" key="labeling/multilineAlign"/>
    <property value="1" key="labeling/multilineHeight"/>
    <property value="Bold" key="labeling/namedStyle"/>
    <property value="true" key="labeling/obstacle"/>
    <property value="1" key="labeling/obstacleFactor"/>
    <property value="0" key="labeling/obstacleType"/>
    <property value="0" key="labeling/offsetType"/>
    <property value="0" key="labeling/placeDirectionSymbol"/>
    <property value="0" key="labeling/placement"/>
    <property value="14" key="labeling/placementFlags"/>
    <property value="false" key="labeling/plussign"/>
    <property value="TR,TL,BR,BL,R,L,TSR,BSR" key="labeling/predefinedPositionOrder"/>
    <property value="true" key="labeling/preserveRotation"/>
    <property value="#ffffff" key="labeling/previewBkgrdColor"/>
    <property value="5" key="labeling/priority"/>
    <property value="2" key="labeling/quadOffset"/>
    <property value="0" key="labeling/repeatDistance"/>
    <property value="0,0,0,0,0,0" key="labeling/repeatDistanceMapUnitScale"/>
    <property value="1" key="labeling/repeatDistanceUnit"/>
    <property value="false" key="labeling/reverseDirectionSymbol"/>
    <property value=">" key="labeling/rightDirectionSymbol"/>
    <property value="10000000" key="labeling/scaleMax"/>
    <property value="1" key="labeling/scaleMin"/>
    <property value="true" key="labeling/scaleVisibility"/>
    <property value="6" key="labeling/shadowBlendMode"/>
    <property value="0" key="labeling/shadowColorB"/>
    <property value="0" key="labeling/shadowColorG"/>
    <property value="0" key="labeling/shadowColorR"/>
    <property value="true" key="labeling/shadowDraw"/>
    <property value="135" key="labeling/shadowOffsetAngle"/>
    <property value="1" key="labeling/shadowOffsetDist"/>
    <property value="true" key="labeling/shadowOffsetGlobal"/>
    <property value="0,0,0,0,0,0" key="labeling/shadowOffsetMapUnitScale"/>
    <property value="1" key="labeling/shadowOffsetUnits"/>
    <property value="1" key="labeling/shadowRadius"/>
    <property value="false" key="labeling/shadowRadiusAlphaOnly"/>
    <property value="0,0,0,0,0,0" key="labeling/shadowRadiusMapUnitScale"/>
    <property value="1" key="labeling/shadowRadiusUnits"/>
    <property value="100" key="labeling/shadowScale"/>
    <property value="68" key="labeling/shadowTransparency"/>
    <property value="0" key="labeling/shadowUnder"/>
    <property value="0" key="labeling/shapeBlendMode"/>
    <property value="255" key="labeling/shapeBorderColorA"/>
    <property value="128" key="labeling/shapeBorderColorB"/>
    <property value="128" key="labeling/shapeBorderColorG"/>
    <property value="128" key="labeling/shapeBorderColorR"/>
    <property value="0" key="labeling/shapeBorderWidth"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeBorderWidthMapUnitScale"/>
    <property value="1" key="labeling/shapeBorderWidthUnits"/>
    <property value="false" key="labeling/shapeDraw"/>
    <property value="255" key="labeling/shapeFillColorA"/>
    <property value="255" key="labeling/shapeFillColorB"/>
    <property value="255" key="labeling/shapeFillColorG"/>
    <property value="255" key="labeling/shapeFillColorR"/>
    <property value="64" key="labeling/shapeJoinStyle"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeOffsetMapUnitScale"/>
    <property value="1" key="labeling/shapeOffsetUnits"/>
    <property value="0" key="labeling/shapeOffsetX"/>
    <property value="0" key="labeling/shapeOffsetY"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeRadiiMapUnitScale"/>
    <property value="1" key="labeling/shapeRadiiUnits"/>
    <property value="0" key="labeling/shapeRadiiX"/>
    <property value="0" key="labeling/shapeRadiiY"/>
    <property value="0" key="labeling/shapeRotation"/>
    <property value="0" key="labeling/shapeRotationType"/>
    <property value="" key="labeling/shapeSVGFile"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeSizeMapUnitScale"/>
    <property value="0" key="labeling/shapeSizeType"/>
    <property value="1" key="labeling/shapeSizeUnits"/>
    <property value="0" key="labeling/shapeSizeX"/>
    <property value="0" key="labeling/shapeSizeY"/>
    <property value="0" key="labeling/shapeTransparency"/>
    <property value="0" key="labeling/shapeType"/>
    <property value="&lt;substitutions/>" key="labeling/substitutions"/>
    <property value="255" key="labeling/textColorA"/>
    <property value="21" key="labeling/textColorB"/>
    <property value="77" key="labeling/textColorG"/>
    <property value="24" key="labeling/textColorR"/>
    <property value="0" key="labeling/textTransp"/>
    <property value="0" key="labeling/upsidedownLabels"/>
    <property value="false" key="labeling/useSubstitutions"/>
    <property value="," key="labeling/wrapChar"/>
    <property value="0" key="labeling/xOffset"/>
    <property value="0" key="labeling/yOffset"/>
    <property value="0" key="labeling/zIndex"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory scaleDependency="Area" enabled="0" sizeType="MM" spacingUnit="MM" width="15" lineSizeType="MM" lineSizeScale="3x:0,0,0,0,0,0" penColor="#000000" backgroundAlpha="255" penAlpha="255" penWidth="0" height="15" minimumSize="0" backgroundColor="#ffffff" direction="1" showAxis="0" spacing="0" rotationOffset="270" labelPlacementMethod="XHeight" sizeScale="3x:0,0,0,0,0,0" scaleBasedVisibility="0" maxScaleDenominator="1e+08" barWidth="5" diagramOrientation="Up" minScaleDenominator="inf" spacingUnitScale="3x:0,0,0,0,0,0" opacity="1">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol force_rhr="0" type="line" name="" clip_to_extent="1" alpha="1">
          <layer class="SimpleLine" enabled="1" locked="0" pass="0">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" priority="0" dist="0" placement="0" zIndex="0" showAll="1" linePlacementFlags="10">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="Name">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Type">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="ASMA_No">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DataSource">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Credit">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="APAD_ID">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Area">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Centr_Lat">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Centr_Long">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Propon">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DesigInstr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Modificati">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="NextReview">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DomainClas">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Hyperlink">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="OrigDesig">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="Name"/>
    <alias index="1" name="" field="Type"/>
    <alias index="2" name="" field="ASMA_No"/>
    <alias index="3" name="" field="DataSource"/>
    <alias index="4" name="" field="Credit"/>
    <alias index="5" name="" field="APAD_ID"/>
    <alias index="6" name="" field="Area"/>
    <alias index="7" name="" field="Centr_Lat"/>
    <alias index="8" name="" field="Centr_Long"/>
    <alias index="9" name="" field="Propon"/>
    <alias index="10" name="" field="DesigInstr"/>
    <alias index="11" name="" field="Modificati"/>
    <alias index="12" name="" field="NextReview"/>
    <alias index="13" name="" field="DomainClas"/>
    <alias index="14" name="" field="Hyperlink"/>
    <alias index="15" name="" field="OrigDesig"/>
  </aliases>
  <defaults>
    <default expression="" field="Name" applyOnUpdate="0"/>
    <default expression="" field="Type" applyOnUpdate="0"/>
    <default expression="" field="ASMA_No" applyOnUpdate="0"/>
    <default expression="" field="DataSource" applyOnUpdate="0"/>
    <default expression="" field="Credit" applyOnUpdate="0"/>
    <default expression="" field="APAD_ID" applyOnUpdate="0"/>
    <default expression="" field="Area" applyOnUpdate="0"/>
    <default expression="" field="Centr_Lat" applyOnUpdate="0"/>
    <default expression="" field="Centr_Long" applyOnUpdate="0"/>
    <default expression="" field="Propon" applyOnUpdate="0"/>
    <default expression="" field="DesigInstr" applyOnUpdate="0"/>
    <default expression="" field="Modificati" applyOnUpdate="0"/>
    <default expression="" field="NextReview" applyOnUpdate="0"/>
    <default expression="" field="DomainClas" applyOnUpdate="0"/>
    <default expression="" field="Hyperlink" applyOnUpdate="0"/>
    <default expression="" field="OrigDesig" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Name"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Type"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="ASMA_No"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="DataSource"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Credit"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="APAD_ID"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Area"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Centr_Lat"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Centr_Long"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Propon"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="DesigInstr"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Modificati"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="NextReview"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="DomainClas"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="Hyperlink"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="OrigDesig"/>
  </constraints>
  <constraintExpressions>
    <constraint field="Name" exp="" desc=""/>
    <constraint field="Type" exp="" desc=""/>
    <constraint field="ASMA_No" exp="" desc=""/>
    <constraint field="DataSource" exp="" desc=""/>
    <constraint field="Credit" exp="" desc=""/>
    <constraint field="APAD_ID" exp="" desc=""/>
    <constraint field="Area" exp="" desc=""/>
    <constraint field="Centr_Lat" exp="" desc=""/>
    <constraint field="Centr_Long" exp="" desc=""/>
    <constraint field="Propon" exp="" desc=""/>
    <constraint field="DesigInstr" exp="" desc=""/>
    <constraint field="Modificati" exp="" desc=""/>
    <constraint field="NextReview" exp="" desc=""/>
    <constraint field="DomainClas" exp="" desc=""/>
    <constraint field="Hyperlink" exp="" desc=""/>
    <constraint field="OrigDesig" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column hidden="0" type="field" width="-1" name="Centr_Lat"/>
      <column hidden="0" type="field" width="-1" name="Centr_Long"/>
      <column hidden="0" type="field" width="-1" name="Propon"/>
      <column hidden="0" type="field" width="-1" name="DesigInstr"/>
      <column hidden="1" type="actions" width="-1"/>
      <column hidden="0" type="field" width="317" name="Name"/>
      <column hidden="0" type="field" width="-1" name="Type"/>
      <column hidden="0" type="field" width="-1" name="ASMA_No"/>
      <column hidden="0" type="field" width="-1" name="DataSource"/>
      <column hidden="0" type="field" width="-1" name="Credit"/>
      <column hidden="0" type="field" width="-1" name="APAD_ID"/>
      <column hidden="0" type="field" width="-1" name="Area"/>
      <column hidden="0" type="field" width="-1" name="Modificati"/>
      <column hidden="0" type="field" width="-1" name="NextReview"/>
      <column hidden="0" type="field" width="-1" name="DomainClas"/>
      <column hidden="0" type="field" width="-1" name="Hyperlink"/>
      <column hidden="0" type="field" width="-1" name="OrigDesig"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>D:/Quantarctica</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable/>
  <labelOnTop/>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE( "Name", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
