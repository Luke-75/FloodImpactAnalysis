import os
from pathlib import Path
from dotenv import load_dotenv

import geopandas as gpd
import folium


def create_map(
    lat: float,
    lon: float,
    analysis_area,
    flood_zones: gpd.GeoDataFrame,
    affected_buildings: gpd.GeoDataFrame
) -> folium.Map:

    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"

    load_dotenv(dotenv_path=env_path)

    carto_api_key = os.getenv("CARTO_BASEMAP_API_KEY")

    #if not carto_api_key:
    #    raise RuntimeError("CARTO basemap API key is not configured.")

    #carto_tiles = (
    #    "https://basemaps.cartocdn.com/rastertiles/"
    #    "light_all/{z}/{x}/{y}.png"
    #    f"?key={carto_api_key}"
    #)

    map = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles=None
    )

    #folium.TileLayer(
        #    tiles=carto_tiles,
        #    attr="© OpenStreetMap contributors © CARTO",
        #    name="CARTO Positron",
        #).add_to(map)

    if carto_api_key:
        carto_tiles = (
            "https://basemaps.cartocdn.com/rastertiles/"
            "light_all/{z}/{x}/{y}.png"
            f"?key={carto_api_key}"
        )

        folium.TileLayer(
            tiles=carto_tiles,
            attr="© OpenStreetMap contributors © CARTO",
            name="CARTO Positron",
        ).add_to(map)


    analysis_area_4326 = gpd.GeoSeries(
        [analysis_area],
        crs="EPSG:5514"
    ).to_crs("EPSG:4326").iloc[0]

    folium.GeoJson(
        analysis_area_4326,
        name="Analysis area",
        style_function=lambda feature: {
            "color": "black",
            "weight": 2,
            "fill": False,
        }
    ).add_to(map)

    flood_zones_4326 = flood_zones.to_crs("EPSG:4326")

    folium.GeoJson(
        flood_zones_4326,
        name="Q100 flood zone",
        style_function=lambda feature: {
            "color": "blue",
            "weight": 1,
            "fillColor": "blue",
            "fillOpacity": 0.35,
        }
    ).add_to(map)

    if not affected_buildings.empty:
        affected_buildings_map = affected_buildings.copy()

        affected_buildings_map["building_area_m2"] = (affected_buildings_map["building_area_m2"].round(1))
        affected_buildings_map["flooded_area_m2"] = (affected_buildings_map["flooded_area_m2"].round(1))
        affected_buildings_map["flooded_pct"] = (affected_buildings_map["flooded_pct"].round(1))

        affected_buildings_4326 = (affected_buildings_map.to_crs("EPSG:4326"))

        folium.GeoJson(
            affected_buildings_4326,
                name="Affected buildings",
                style_function=lambda feature: {
                    "color": "red",
                    "weight": 1,
                    "fillColor": "red",
                    "fillOpacity": 0.7,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[
                        "building_area_m2",
                        "flooded_area_m2",
                        "flooded_pct",
                    ],
                    aliases=[
                        "Building area (m²):",
                        "Flooded area (m²):",
                        "Flooded (%):",
                    ],
                    localize=True,
                    sticky=False,
                ),
        ).add_to(map)
        
    min_lon, min_lat, max_lon, max_lat = analysis_area_4326.bounds

    map.fit_bounds([
        [min_lat, min_lon],
        [max_lat, max_lon]
    ])

    folium.LayerControl().add_to(map)

    return map


