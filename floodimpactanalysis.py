from src.flimpanal_geo import geocode, create_bbox, get_q100_flood_zones, get_buildings, split_bbox, to_wgs84, prepare_buildings, find_affected_buildings, prepare_flood_zones, retrieve_buildings, analyze_location
from shapely.geometry import box
from src.flimpanal_map import create_map
import streamlit as st
import streamlit.components.v1 as components


lat, lon, analysis_area, flood_zones, buildings, affected_buildings = analyze_location("Prague", 2)

print(f"Total buildings: {len(buildings)}")
print(f"Flood area: {flood_zones.geometry.area.sum():.2f} m²")
print(f"Affected buildings: {len(affected_buildings)}")

flood_map = create_map(lat, lon, analysis_area, flood_zones, affected_buildings)

html = flood_map.get_root().render()

st.write(f"Map HTML size: {len(html):,} characters")

components.html(
    flood_map.get_root().render(),
    height=650,
    scrolling=False,
)

#flood_map.save("flood_impact_map.html")


