# Flood Impact Analysis

A geospatial application for identifying buildings whose footprints intersect Q100 flood zones in the Czech Republic. It calculates building exposure and displays the analysis area, flood zone, and affected buildings on an interactive map.

## Features

- Search for a location and define an analysis radius.
- Retrieve Q100 flood-zone geometry for the selected area.
- Retrieve building footprints from OpenStreetMap.
- Identify buildings with positive-area overlap with the flood zone.
- Calculate total and flooded building footprint area and percentage exposure.
- Display flood zones, affected buildings, and the analysis area on an interactive map.
- Validate that the complete analysis area lies within the Czech Republic.


## Data Limitations

- The analysis is currently limited to areas entirely within the Czech Republic.
- Flood exposure is based on the Q100 flood-zone dataset, representing areas associated with a 1% annual exceedance probability.
- A building is considered affected when its footprint has a positive-area geometric overlap with the Q100 flood zone. This represents spatial exposure, not an assessment of structural damage or flood risk to occupants.
- VÚV flood-zone polygons are orientational. For authoritative information about the exact extent of a flood zone, consult the relevant water authority or watercourse administrator.
- Building footprints are obtained from OpenStreetMap and their availability and accuracy depend on the underlying OSM data.


## How It Works

geocode
   ↓
create analysis area
   ↓
validate Czech coverage
   ├── invalid → stop
   │
   └── valid
        ↓
      VÚV request
        ↓
      OSM request
        ↓
      analysis


## Architecture

FloodImpactAnalysis/
├── data/
│   └── czech_republic.geojson
├── src/
│   ├── flimpanal_geo.py
│   ├── flimpanal_map.py
│   └── flimpanal_ui.py


## External Services/Data Used

Nominatim                                       → location geocoding
Natural Earth                                   → Czech Republic coverage validation
Výzkumný ústav vodohospodářský (VÚV)            → Q100 flood-zone geometry
OpenStreetMap                                   → building footprints

### Nominatim

Used for forward geocoding of user-entered locations.

This application uses the public Nominatim service operated by the OpenStreetMap Foundation. Use of the public service is subject to the Nominatim Usage Policy, including an absolute maximum of one request per second and use of an identifying User-Agent.

Nominatim Usage Policy:
https://operations.osmfoundation.org/policies/nominatim/


### Natural Earth

Used to validate that the complete analysis area lies within the Czech Republic.

The application uses the Natural Earth 1:10m Admin 0 Countries dataset. Natural Earth vector and raster data is in the public domain.

Natural Earth Terms of Use:
https://www.naturalearthdata.com/about/terms-of-use/


### OpenStreetMap

Used as the source of building footprints.

OpenStreetMap data is licensed under the Open Data Commons Open Database License (ODbL). OpenStreetMap and its contributors must be credited when the data is used.

© OpenStreetMap contributors

Copyright and License:
https://www.openstreetmap.org/copyright


### Výzkumný ústav vodohospodářský T. G. Masaryka (VÚV TGM)

Used as the source of Q100 flood-zone geometry for the Czech Republic.

The flood-zone dataset is provided under Creative Commons BY 4.0. Source attribution is required when the data is presented.

Source: Výzkumný ústav vodohospodářský T. G. Masaryka, v.v.i. (VÚV TGM)

The flood-zone polygons provided by this dataset are orientational. For authoritative information about the exact extent of a flood zone, consult the relevant water authority or watercourse administrator.

Flood-zone metadata:
https://heis.vuv.cz/xmicka/record/basic/CZ-VUV-MD-ZaplavUzemi

