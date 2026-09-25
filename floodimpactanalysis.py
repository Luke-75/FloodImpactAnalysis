from src.flimpanal_geo import geocode, create_bbox, get_q100_flood_zones, get_buildings, split_bbox, to_wgs84, prepare_buildings, find_affected_buildings, prepare_flood_zones, retrieve_buildings
import geopandas as gpd
from shapely.geometry import box
import pandas as pd


lat, lon = geocode("Prague")

bbox = create_bbox(lat, lon, 2)
result = get_q100_flood_zones(bbox)

#print(flood_zones)
#print(f"CRS: {flood_zones.crs}")
#print(f"Geometry types: {flood_zones.geometry.geom_type.tolist()}")
#print(f"Bounds: {flood_zones.total_bounds}")

min_x, min_y, max_x, max_y = bbox
analysis_area = box(min_x, min_y, max_x, max_y)

#print(f"Clipped geometry types: {clipped_flood_zones.geometry.geom_type.tolist()}")
#print(f"Clipped bounds: {clipped_flood_zones.total_bounds}")
#print(f"Clipped area: {clipped_flood_zones.geometry.area.sum():,.0f} m²")

######tiles = split_bbox(bbox)
######building_tiles = []

######for i, tile in enumerate(tiles, start=1):
######    tile_4326 = to_wgs84(tile)
######
######    print(f"\nRetrieving tile {i}...")
######
######    buildings = get_buildings(tile_4326)
######
######    print(f"Tile {i}: {len(buildings)} buildings")
######    #print(buildings.index.names)
######    #print(buildings.index[:10])
######
######    building_tiles.append(buildings)

building_tiles = retrieve_buildings(bbox)
buildings = prepare_buildings(building_tiles, analysis_area)

print(f"Prepared buildings: {len(buildings)}")
print(f"Buildings CRS: {buildings.crs}")
print(buildings.geometry.geom_type.value_counts())
print(f"Building bounds: {buildings.total_bounds}")

flood_data = get_q100_flood_zones(bbox)
flood_zones = prepare_flood_zones(flood_data, analysis_area)

print(f"Prepared flood zones: {len(flood_zones)}")
print(f"Flood CRS: {flood_zones.crs}")
print(f"Flood area: {flood_zones.geometry.area.sum():.2f} m²")
print(f"Flood bounds: {flood_zones.total_bounds}")

affected_buildings = find_affected_buildings(buildings, flood_zones)

print(f"Total buildings: {len(buildings)}")
print(f"Affected buildings: {len(affected_buildings)}")

print(affected_buildings["flooded_area_m2"].describe())
print(
    "Zero-area intersections:",
    (affected_buildings["flooded_area_m2"] == 0).sum()
)

print(
    affected_buildings["flooded_area_m2"]
    .sort_values()
    .head(10)
)


print(
    affected_buildings[
        ["building_area_m2", "flooded_area_m2", "flooded_pct"]
    ].describe()
)

print(
    affected_buildings[
        ["building_area_m2", "flooded_area_m2", "flooded_pct"]
    ]
    .sort_values("flooded_pct")
    .head(10)
)


print("<= 1%:",
      (affected_buildings["flooded_pct"] <= 1).sum())

print("> 1% and <= 10%:",
      (
          (affected_buildings["flooded_pct"] > 1) &
          (affected_buildings["flooded_pct"] <= 10)
      ).sum())

print("> 10% and < 100%:",
      (
          (affected_buildings["flooded_pct"] > 10) &
          (affected_buildings["flooded_pct"] < 99.999)
      ).sum())

print("~100%:",
      (affected_buildings["flooded_pct"] >= 99.999).sum())



