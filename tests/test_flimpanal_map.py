import geopandas as gpd
import folium
from shapely.geometry import box

import src.flimpanal_map as flimpanal_map
import pytest


@pytest.fixture(autouse=True)
def carto_api_key(monkeypatch):
    monkeypatch.setenv(
        "CARTO_BASEMAP_API_KEY",
        "test-carto-api-key"
    )




def test_create_map_with_no_flood_zones():
    analysis_area = box(0, 0, 100, 100)

    flood_zones = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:5514"
    )

    affected_buildings = gpd.GeoDataFrame(
        {
            "building_area_m2": [],
            "flooded_area_m2": [],
            "flooded_pct": [],
        },
        geometry=[],
        crs="EPSG:5514"
    )

    result = flimpanal_map.create_map(
        lat=50.0,
        lon=14.0,
        analysis_area=analysis_area,
        flood_zones=flood_zones,
        affected_buildings=affected_buildings,
    )

    html = result.get_root().render()

    assert isinstance(result, folium.Map)
    assert isinstance(html, str)
    assert len(html) > 0



def test_create_map_with_flood_zone_and_no_affected_buildings():
    analysis_area = box(0, 0, 100, 100)

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(20, 20, 80, 80)],
        crs="EPSG:5514"
    )

    affected_buildings = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:5514"
    )

    result = flimpanal_map.create_map(
        lat=50.0,
        lon=14.0,
        analysis_area=analysis_area,
        flood_zones=flood_zones,
        affected_buildings=affected_buildings,
    )

    html = result.get_root().render()

    assert isinstance(result, folium.Map)
    assert isinstance(html, str)
    assert len(html) > 0



#def test_create_map_includes_carto_basemap(monkeypatch):
def test_create_map_includes_carto_basemap():
    #monkeypatch.setenv(
    #    "CARTO_BASEMAP_API_KEY",
    #    "test-carto-api-key"
    #)

    analysis_area = box(0, 0, 100, 100)

    flood_zones = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:5514"
    )

    affected_buildings = gpd.GeoDataFrame(
        {
            "building_area_m2": [],
            "flooded_area_m2": [],
            "flooded_pct": [],
        },
        geometry=[],
        crs="EPSG:5514"
    )

    result = flimpanal_map.create_map(
        lat=50.0,
        lon=14.0,
        analysis_area=analysis_area,
        flood_zones=flood_zones,
        affected_buildings=affected_buildings,
    )

    html = result.get_root().render()

    assert "CARTO Positron" in html
    assert "test-carto-api-key" in html    



def test_create_map_without_carto_key(monkeypatch):
    monkeypatch.delenv(
        "CARTO_BASEMAP_API_KEY",
        raising=False
    )
    monkeypatch.setattr(
        flimpanal_map,
        "load_dotenv",
        lambda **kwargs: None
    )

    analysis_area = box(0, 0, 100, 100)

    flood_zones = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:5514"
    )

    affected_buildings = gpd.GeoDataFrame(
        {
            "building_area_m2": [],
            "flooded_area_m2": [],
            "flooded_pct": [],
        },
        geometry=[],
        crs="EPSG:5514"
    )

    result = flimpanal_map.create_map(
        lat=50.0,
        lon=14.0,
        analysis_area=analysis_area,
        flood_zones=flood_zones,
        affected_buildings=affected_buildings,
    )

    html = result.get_root().render()

    assert isinstance(result, folium.Map)
    assert "CARTO Positron" not in html    


