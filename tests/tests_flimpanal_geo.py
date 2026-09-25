import geopandas as gpd
import pytest
from shapely.geometry import box, Polygon, Point, LineString
import pandas as pd

import src.flimpanal_geo as flimpanal_geo


def test_find_affected_building_with_50_percent_overlap():
    buildings = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:5514"
    )

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(0, 0, 5, 10)],
        crs="EPSG:5514"
    )

    result = flimpanal_geo.find_affected_buildings(
        buildings,
        flood_zones
    )

    assert len(result) == 1

    building = result.iloc[0]

    assert building["building_area_m2"] == pytest.approx(100)
    assert building["flooded_area_m2"] == pytest.approx(50)
    assert building["flooded_pct"] == pytest.approx(50)



def test_find_affected_building_with_no_overlap():
    buildings = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:5514"
    )

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(20, 20, 30, 30)],
        crs="EPSG:5514"
    )

    result = flimpanal_geo.find_affected_buildings(
        buildings,
        flood_zones
    )

    assert len(result) == 0


def test_find_affected_building_with_100_percent_overlap():
    buildings = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:5514"
    )

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(-5, -5, 15, 15)],
        crs="EPSG:5514"
    )

    result = flimpanal_geo.find_affected_buildings(
        buildings,
        flood_zones
    )

    assert len(result) == 1

    building = result.iloc[0]

    assert building["building_area_m2"] == pytest.approx(100)
    assert building["flooded_area_m2"] == pytest.approx(100)
    assert building["flooded_pct"] == pytest.approx(100)


def test_find_affected_building_touching_flood_boundary():
    buildings = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:5514"
    )

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(10, 0, 20, 10)],
        crs="EPSG:5514"
    )

    result = flimpanal_geo.find_affected_buildings(
        buildings,
        flood_zones
    )

    print(result[
        ["building_area_m2", "flooded_area_m2", "flooded_pct"]
    ])



def test_find_affected_building_touching_flood_boundary():
    buildings = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:5514"
    )

    flood_zones = gpd.GeoDataFrame(
        geometry=[box(10, 0, 20, 10)],
        crs="EPSG:5514"
    )

    result = flimpanal_geo.find_affected_buildings(
        buildings,
        flood_zones
    )

    assert len(result) == 0


def test_prepare_flood_zones_clips_to_analysis_area():
    flood_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Test flood"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-5, -5],
                        [15, -5],
                        [15, 15],
                        [-5, 15],
                        [-5, -5],
                    ]]
                },
            }
        ],
    }

    analysis_area = box(0, 0, 10, 10)

    result = flimpanal_geo.prepare_flood_zones(
        flood_data,
        analysis_area
    )

    assert len(result) == 1
    assert result.crs.to_epsg() == 5514
    assert result.geometry.area.iloc[0] == pytest.approx(100)
    assert tuple(result.total_bounds) == pytest.approx(
        (0, 0, 10, 10)
    )



def test_retrieve_buildings_retrieves_four_tiles(monkeypatch):

    bbox = (0, 0, 4000, 4000)

    calls = []

    def fake_get_buildings(tile):
        calls.append(tile)

        return gpd.GeoDataFrame(
            geometry=[box(0, 0, 1, 1)],
            crs="EPSG:4326"
        )

    monkeypatch.setattr(
        flimpanal_geo,
        "get_buildings",
        fake_get_buildings
    )

    result = flimpanal_geo.retrieve_buildings(bbox)

    assert len(result) == 4
    assert len(calls) == 4

    assert all(
        isinstance(tile, Polygon)
        for tile in calls
    )

    assert len({
        tile.wkt
        for tile in calls
    }) == 4



def test_prepare_buildings_removes_duplicate_osm_features():

    index = pd.MultiIndex.from_tuples(
        [
            ("way", 100),
            ("way", 200),
        ],
        names=["element", "id"]
    )

    tile_1 = gpd.GeoDataFrame(
        geometry=[
            box(0, 0, 10, 10),
            box(20, 0, 30, 10),
        ],
        index=index,
        crs="EPSG:5514"
    )

    tile_2 = gpd.GeoDataFrame(
        geometry=[
            box(0, 0, 10, 10),
        ],
        index=pd.MultiIndex.from_tuples(
            [("way", 100)],
            names=["element", "id"]
        ),
        crs="EPSG:5514"
    )

    analysis_area = box(-10, -10, 40, 20)

    result = flimpanal_geo.prepare_buildings(
        [tile_1, tile_2],
        analysis_area
    )

    assert len(result) == 2
    assert ("way", 100) in result.index
    assert ("way", 200) in result.index



def test_prepare_buildings_removes_non_polygon_geometries():
    index = pd.MultiIndex.from_tuples(
        [
            ("way", 100),
            ("node", 200),
            ("way", 300),
        ],
        names=["element", "id"]
    )

    tile = gpd.GeoDataFrame(
        geometry=[
            box(0, 0, 10, 10),
            Point(5, 5),
            LineString([(0, 0), (10, 10)]),
        ],
        index=index,
        crs="EPSG:5514"
    )

    analysis_area = box(-10, -10, 20, 20)

    result = flimpanal_geo.prepare_buildings(
        [tile],
        analysis_area
    )

    assert len(result) == 1
    assert ("way", 100) in result.index
    assert result.geometry.iloc[0].geom_type == "Polygon"



def test_prepare_buildings_preserves_full_building_geometry():
    index = pd.MultiIndex.from_tuples(
        [("way", 100)],
        names=["element", "id"]
    )

    tile = gpd.GeoDataFrame(
        geometry=[box(5, 0, 15, 10)],
        index=index,
        crs="EPSG:5514"
    )

    analysis_area = box(0, 0, 10, 10)

    result = flimpanal_geo.prepare_buildings(
        [tile],
        analysis_area
    )

    assert len(result) == 1

    building = result.geometry.iloc[0]

    assert building.area == pytest.approx(100)
    assert building.bounds == pytest.approx(
        (5, 0, 15, 10)
    )


