from src.flimpanal_geo import geocode, create_bbox, get_q100_flood_zones, get_buildings, split_bbox, to_wgs84
import geopandas as gpd
from shapely.geometry import box
import pandas as pd


lat, lon = geocode("Prague")

bbox = create_bbox(lat, lon, 2)
result = get_q100_flood_zones(bbox)
flood_zones = gpd.GeoDataFrame.from_features(
    result["features"],
    crs="EPSG:5514"
)

#print(flood_zones)
#print(f"CRS: {flood_zones.crs}")
#print(f"Geometry types: {flood_zones.geometry.geom_type.tolist()}")
#print(f"Bounds: {flood_zones.total_bounds}")

min_x, min_y, max_x, max_y = bbox
analysis_area = box(min_x, min_y, max_x, max_y)

clipped_flood_zones = gpd.clip(flood_zones, analysis_area)

#print(f"Clipped geometry types: {clipped_flood_zones.geometry.geom_type.tolist()}")
#print(f"Clipped bounds: {clipped_flood_zones.total_bounds}")
#print(f"Clipped area: {clipped_flood_zones.geometry.area.sum():,.0f} m²")

"""
analysis_area_4326 = gpd.GeoSeries(
    [analysis_area],
    crs="EPSG:5514"
).to_crs("EPSG:4326").iloc[0]

print(analysis_area_4326)
print(analysis_area_4326.bounds)
"""

tiles = split_bbox(bbox)
building_tiles = []

for i, tile in enumerate(tiles, start=1):
    tile_4326 = to_wgs84(tile)

    print(f"\nRetrieving tile {i}...")

    buildings = get_buildings(tile_4326)

    print(f"Tile {i}: {len(buildings)} buildings")
    #print(buildings.index.names)
    #print(buildings.index[:10])

    building_tiles.append(buildings)

all_buildings = pd.concat(building_tiles)

print(f"Buildings before deduplication: {len(all_buildings)}")
print(f"Duplicate OSM features: {all_buildings.index.duplicated().sum()}")

unique_buildings = all_buildings[
    ~all_buildings.index.duplicated(keep="first")
]

print(f"Unique buildings: {len(unique_buildings)}")

print(type(unique_buildings))
print(unique_buildings.crs)

buildings_5514 = unique_buildings.to_crs("EPSG:5514")

buildings_clipped = gpd.clip(
    buildings_5514,
    analysis_area
)

buildings_clipped = buildings_clipped[
    buildings_clipped.geometry.geom_type.isin(
        ["Polygon", "MultiPolygon"]
    )
].copy()

print(f"Unique OSM features: {len(unique_buildings)}")
print(f"Usable buildings after clipping: {len(buildings_clipped)}")
print(buildings_clipped.geometry.geom_type.value_counts())
print(f"Buildings CRS: {buildings_clipped.crs}")
print(f"Building bounds: {buildings_clipped.total_bounds}")

flood_area = clipped_flood_zones.geometry.union_all()

affected_buildings = buildings_clipped[
    buildings_clipped.geometry.intersects(flood_area)
].copy()

print(f"Total buildings: {len(buildings_clipped)}")
print(f"Affected buildings: {len(affected_buildings)}")

affected_buildings["flooded_area_m2"] = (
    affected_buildings.geometry
    .intersection(flood_area)
    .area
)

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


affected_buildings["building_area_m2"] = (
    affected_buildings.geometry.area
)

affected_buildings["flooded_pct"] = (
    affected_buildings["flooded_area_m2"]
    / affected_buildings["building_area_m2"]
    * 100
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

"""
test_bbox = (-744809.66, -1045012.86, -742809.66, -1043012.86)
min_x, min_y, max_x, max_y = test_bbox
analysis_area = box(min_x, min_y, max_x, max_y)
analysis_area_4326 = gpd.GeoSeries(
    [analysis_area],
    crs="EPSG:5514"
).to_crs("EPSG:4326").iloc[0]

buildings = get_buildings(analysis_area_4326)

print(f"Buildings retrieved: {len(buildings)}")
print(f"Buildings CRS: {buildings.crs}")
print(buildings.geometry.geom_type.value_counts())
"""

"""
buildings_5514 = buildings.to_crs("EPSG:5514")

buildings_clipped = gpd.clip(
    buildings_5514,
    analysis_area
)

print(f"Buildings retrieved: {len(buildings_5514)}")
print(f"Buildings after clipping: {len(buildings_clipped)}")
print(f"Building geometry types:")
print(buildings_clipped.geometry.geom_type.value_counts())
print(f"Building bounds: {buildings_clipped.total_bounds}")

buildings_clipped = buildings_clipped[
    buildings_clipped.geometry.geom_type.isin(
        ["Polygon", "MultiPolygon"]
    )
].copy()

print(f"Usable building footprints: {len(buildings_clipped)}")
print(buildings_clipped.geometry.geom_type.value_counts())
"""


