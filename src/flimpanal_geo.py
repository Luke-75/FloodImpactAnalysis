# geo.py

from dotenv import load_dotenv
import os
from pathlib import Path
from pyproj import Transformer
import requests
import geopandas as gpd
import osmnx as ox
from shapely.geometry import box
import pandas as pd

# TODO: Validate that the analysis area is within the Czech Republic.
# VUV flood-zone data used by this application only covers Czech territory.


VUV_WFS_URL = (
    "https://ags2.vuv.cz/arcgis/services/isvs_voda/"
    "isvs_voda/MapServer/WFSServer"
)

VUV_Q100_QUERY_URL = (
    "https://ags2.vuv.cz/arcgis/rest/services/"
    "isvs_voda/isvs_voda/MapServer/13/query"
)


def geocode(address: str) -> tuple[float, float]:
    from geopy.geocoders import Nominatim

    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"

    load_dotenv(dotenv_path=env_path)
    user_agent_name = os.getenv("NOMINATIM_USER_AGENT_NAME")
    if not user_agent_name:
            raise RuntimeError("Nominatim user agent name is not configured.")
    
    geolocator = Nominatim(user_agent=user_agent_name)
    location = geolocator.geocode(
        query = address
    )
    if location:
        #return{
        #    location.latitude,
        #    location.longitude 
        #}
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Could not find location for address: {address}")


def create_bbox(
    lat_4326: float,
    lon_4326: float,
    radius_km: float
) -> tuple[float, float, float, float]:

    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:5514",
        always_xy=True
    )

    x_5514, y_5514 = transformer.transform(lon_4326, lat_4326)

    radius_m = radius_km * 1000

    min_x = x_5514 - radius_m
    min_y = y_5514 - radius_m
    max_x = x_5514 + radius_m
    max_y = y_5514 + radius_m

    return min_x, min_y, max_x, max_y

"""
# the WFS query did not return any results, switched to REST
def get_q100_flood_zones(
    bbox: tuple[float, float, float, float]
) -> str:

    min_x, min_y, max_x, max_y = bbox

    vuv_wfs_query_params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "ZaplavUzemi_Q100",
        "bbox": f"{min_y},{min_x},{max_y},{max_x},EPSG:5514",
        #"bbox": f"{min_x},{min_y},{max_x},{max_y},EPSG:5514",
    }

    response = requests.get(VUV_WFS_URL, params=vuv_wfs_query_params, timeout=30)
    response.raise_for_status()

    return response.text
"""

def get_q100_flood_zones(
    bbox: tuple[float, float, float, float]
) -> str:

    min_x, min_y, max_x, max_y = bbox

    params = {
        "where": "1=1",
        "geometry": f"{min_x},{min_y},{max_x},{max_y}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "5514",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "5514",
        "f": "geojson",
    }

    response = requests.get(
        VUV_Q100_QUERY_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def get_buildings(analysis_area):

    tags = {"building": True}

    buildings = ox.features_from_polygon(
        analysis_area,
        tags=tags
    )

    return buildings


def split_bbox(
    bbox: tuple[float, float, float, float]
):
    min_x, min_y, max_x, max_y = bbox

    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    return [
        box(min_x, min_y, mid_x, mid_y),
        box(mid_x, min_y, max_x, mid_y),
        box(min_x, mid_y, mid_x, max_y),
        box(mid_x, mid_y, max_x, max_y),
    ]


def to_wgs84(geometry, source_crs="EPSG:5514"):
    return gpd.GeoSeries(
        [geometry],
        crs=source_crs
    ).to_crs("EPSG:4326").iloc[0]


def prepare_buildings(
    building_tiles: list[gpd.GeoDataFrame],
    analysis_area
) -> gpd.GeoDataFrame:

    # concatenate retrieved tiles --> all buildings
    buildings = pd.concat(building_tiles)

    # dedupliction
    buildings = buildings[
        ~buildings.index.duplicated(keep="first")
    ].copy()

    buildings = buildings.to_crs("EPSG:5514")

    # filtering out streets, etc.
    buildings = buildings[
        buildings.geometry.geom_type.isin(
            ["Polygon", "MultiPolygon"]
        )
    ].copy()

    # list of buildings in the area of analysis
    buildings = buildings[
        buildings.geometry.intersects(analysis_area)
    ].copy()

    return buildings



def find_affected_buildings(
    buildings: gpd.GeoDataFrame,
    flood_zones: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:

    flood_area = flood_zones.geometry.union_all()

    affected = buildings[
        buildings.geometry.intersects(flood_area)
    ].copy()

    affected["building_area_m2"] = affected.geometry.area

    affected["flooded_area_m2"] = (
        affected.geometry
        .intersection(flood_area)
        .area
    )

    affected = affected[
        affected["flooded_area_m2"] > 0
    ].copy()

    affected["flooded_pct"] = (
        affected["flooded_area_m2"]
        / affected["building_area_m2"]
        * 100
    )

    return affected


def prepare_flood_zones(
    flood_data: dict,
    analysis_area
) -> gpd.GeoDataFrame:

    flood_zones = gpd.GeoDataFrame.from_features(
        flood_data["features"],
        crs="EPSG:5514"
    )

    flood_zones = gpd.clip(
        flood_zones,
        analysis_area
    )

    return flood_zones


def retrieve_buildings(
    bbox: tuple[float, float, float, float]
) -> list[gpd.GeoDataFrame]:

    tiles = split_bbox(bbox)
    building_tiles = []

    for i, tile in enumerate(tiles, start=1):
        print(f"Retrieving tile {i}...")

        tile_4326 = to_wgs84(tile)

        buildings = get_buildings(tile_4326)

        print(f"Tile {i}: {len(buildings)} buildings")

        building_tiles.append(buildings)

    return building_tiles



def analyze_location(
    location: str,
    radius_km: float
):
    lat, lon = geocode(location)

    bbox = create_bbox(lat, lon, radius_km)
    analysis_area = box(*bbox)

    flood_data = get_q100_flood_zones(bbox)
    flood_zones = prepare_flood_zones(flood_data, analysis_area)

    building_tiles = retrieve_buildings(bbox)
    buildings = prepare_buildings(building_tiles, analysis_area)

    affected_buildings = find_affected_buildings(buildings, flood_zones)

    return (
        lat,
        lon,
        analysis_area,
        flood_zones,
        buildings,
        affected_buildings,
    )


