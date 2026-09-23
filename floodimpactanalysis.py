from src.flimpanal_geo import geocode, create_bbox, get_q100_flood_zones
import geopandas as gpd
from shapely.geometry import box


lat, lon = geocode("Prague")

bbox = create_bbox(lat, lon, 2)

print(f"Location: latitude {lat}, longitude {lon}")
print(f"BBOX: {bbox}")

result = get_q100_flood_zones(bbox)

print(result.keys())
print(f"Number of features: {len(result['features'])}")

for feature in result["features"]:
    print(feature["properties"])


"""
test_bbox = (
    -741000,
    -1054000,
    -739000,
    -1053000,
)

result = get_q100_flood_zones(test_bbox)
print(result[:1000])
"""

flood_zones = gpd.GeoDataFrame.from_features(
    result["features"],
    crs="EPSG:5514"
)

print(flood_zones)
print(f"CRS: {flood_zones.crs}")
print(f"Geometry types: {flood_zones.geometry.geom_type.tolist()}")
print(f"Bounds: {flood_zones.total_bounds}")


min_x, min_y, max_x, max_y = bbox
analysis_area = box(min_x, min_y, max_x, max_y)

clipped_flood_zones = gpd.clip(flood_zones, analysis_area)

print(f"Clipped geometry types: {clipped_flood_zones.geometry.geom_type.tolist()}")
print(f"Clipped bounds: {clipped_flood_zones.total_bounds}")
print(f"Clipped area: {clipped_flood_zones.geometry.area.sum():,.0f} m²")
