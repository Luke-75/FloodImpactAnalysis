"""
download 
from https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip
to </project_root>/data/ 

extract the ZIP archive to </project_root>/data/ne_10m_admin_0_countries/

data/
└── ne_10m_admin_0_countries/
    ├── ne_10m_admin_0_countries.shp
    ├── ne_10m_admin_0_countries.dbf
    ├── ne_10m_admin_0_countries.shx
    ├── ne_10m_admin_0_countries.prj
    └── ...
"""

# This file should be run from the project root

import geopandas as gpd

# show all the DBF fields

world = gpd.read_file(
    "data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
)

print(world.columns.tolist())

# inspect records that look Czech-related

print(
    world[
        world["NAME"].str.contains("Czech", case=False, na=False)
    ].to_string()
)

# show the source CRS and geometry types before transforming anything

print(world.crs)
print(world.geom_type.value_counts())

"""
EPSG:4326
MultiPolygon    151
Polygon         107
Name: count, dtype: int64
"""

"""
important fields:

NAME       = Czechia
ADMIN      = Czechia
ADM0_A3    = CZE
ISO_A2     = CZ
ISO_A3     = CZE
geometry   = Polygon
"""

czechia = world[
    world["ADM0_A3"] == "CZE"
].copy()

print(len(czechia))
print(czechia[["NAME", "ADMIN", "ADM0_A3", "ISO_A2", "ISO_A3"]])
print(czechia.crs)
print(czechia.geometry.iloc[0].geom_type)

"""
1
       NAME    ADMIN ADM0_A3 ISO_A2 ISO_A3
48  Czechia  Czechia     CZE     CZ    CZE
EPSG:4326
Polygon
"""

# extracting and saving the cuntry borders

czechia = czechia[
    ["ADM0_A3", "geometry"]
]

czechia.to_file(
    "data/czech_republic.geojson",
    driver="GeoJSON"
)

# download integrity verification

check = gpd.read_file("data/czech_republic.geojson")

print(check)
print(check.crs)
print(check.geometry.iloc[0].geom_type)
print(check.total_bounds)

"""
  ADM0_A3                                           geometry
0     CZE  POLYGON ((14.81039 50.85845, 14.83168 50.85798...
EPSG:4326
Polygon
[12.07614099 48.55791575 18.83743372 51.04001231]
"""

print(czechia)
print("CRS:", czechia.crs)
print("Rows:", len(czechia))
print("Geometry:", czechia.geometry.iloc[0].geom_type)
print("Valid:", czechia.geometry.iloc[0].is_valid)
print("Bounds:", czechia.total_bounds)

"""
   ADM0_A3                                           geometry
48     CZE  POLYGON ((14.81039 50.85845, 14.83168 50.85798...
CRS: EPSG:4326
Rows: 1
Geometry: Polygon
Valid: True
Bounds: [12.07614099 48.55791575 18.83743372 51.04001231]
"""


