from src.flimpanal_geo import geocode, create_bbox, get_q100_flood_zones, get_buildings, split_bbox, to_wgs84, prepare_buildings, find_affected_buildings, prepare_flood_zones, retrieve_buildings
from shapely.geometry import box


lat, lon = geocode("Prague")

bbox = create_bbox(lat, lon, 2)
analysis_area = box(*bbox)
building_tiles = retrieve_buildings(bbox)
buildings = prepare_buildings(building_tiles, analysis_area)

flood_data = get_q100_flood_zones(bbox)
flood_zones = prepare_flood_zones(flood_data, analysis_area)

affected_buildings = find_affected_buildings(buildings, flood_zones)

print(f"Total buildings: {len(buildings)}")
print(f"Flood area: {flood_zones.geometry.area.sum():.2f} m²")
print(f"Affected buildings: {len(affected_buildings)}")



