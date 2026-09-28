import geopandas as gpd
import folium

"""
def create_map(lat: float, lon: float) -> folium.Map:
    return folium.Map(
        location=[lat, lon],
        zoom_start=13
    )
"""

"""
def create_map(lat: float, lon: float) -> folium.Map:
    return folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles="CartoDB positron"
    )
"""


def create_map(
    lat: float,
    lon: float,
    analysis_area,
    flood_zones: gpd.GeoDataFrame,
    affected_buildings: gpd.GeoDataFrame
) -> folium.Map:

    map = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles=None
    )

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

    
    affected_buildings_map = affected_buildings.copy()

    affected_buildings_map["building_area_m2"] = (affected_buildings_map["building_area_m2"].round(1))
    affected_buildings_map["flooded_area_m2"] = (affected_buildings_map["flooded_area_m2"].round(1))
    affected_buildings_map["flooded_pct"] = (affected_buildings_map["flooded_pct"].round(1))

    #affected_buildings_4326 = affected_buildings.to_crs("EPSG:4326")
    affected_buildings_4326 = affected_buildings_map.to_crs("EPSG:4326")
      
    """
    folium.GeoJson(
        affected_buildings_4326,
        name="Affected buildings",
        style_function=lambda feature: {
            "color": "red",
            "weight": 1,
            "fillColor": "red",
            "fillOpacity": 0.7,
        }
    ).add_to(map)
    """

    if not affected_buildings_4326.empty:
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


