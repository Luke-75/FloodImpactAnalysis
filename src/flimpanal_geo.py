# geo.py

from dotenv import load_dotenv
import os
from pathlib import Path
from pyproj import Transformer
import requests
import geopandas as gpd


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
        return{
            location.latitude,
            location.longitude 
        }
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

