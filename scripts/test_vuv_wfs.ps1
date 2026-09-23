# PowerShell WFS investigation script
# PS commands to test the VUV WFS functionality

#
# The VUV metadata gives this WFS endpoint:
#
# VUV flood-zone WFS service
# https://ags2.vuv.cz/arcgis/services/isvs_voda/isvs_voda/MapServer/WFSServer?utm_source=chatgpt.com
#
# WFS (Web Feature Service) is different from WMS in an important way:
#
# WMS  - provides rendered map imagery
# WFS  - provides the actual geographic features/geometries
#
#
# The dataset covers the Czech Republic and is vector data. 
# The metadata describes flood-zone layers for Q5, Q20, Q100, Q500 and active zones. It says the data originate from flood-zone determinations supplied by water authorities and that updates should occur at the beginning of each quarter depending on updates to the source files.
#
# The metadata record currently gives a revision date of 31 August 2025, with metadata updated on 30 October 2025.
#
# There are also direct Shapefile downloads for Q5, Q20, Q100 and active zones, in case a local/offline fallback is needed.
#
# Licensing looks friendly for a public GitHub portfolio: the metadata specifies CC BY 4.0, with attribution required.
#
# Limitations:
# VUV explicitly says the polygon boundaries in this layer are orientational, and authoritative information about the exact boundary should be obtained from the relevant water authority or watercourse administrator. 
# 

Invoke-WebRequest `
  -Uri "https://ags2.vuv.cz/arcgis/services/isvs_voda/isvs_voda/MapServer/WFSServer?service=WFS&request=GetCapabilities" `
  -OutFile "capabilities.xml"

Get-Item .\capabilities.xml
Get-Content .\capabilities.xml -TotalCount 20

# --> Iw everything works, the endpoint is alive and returning a valid WFS 2.0.0 capabilities document

# What feature types does the WFS expose?

[xml]$wfs = Get-Content .\capabilities.xml -Raw

$ns = New-Object System.Xml.XmlNamespaceManager($wfs.NameTable)
$ns.AddNamespace("wfs", "http://www.opengis.net/wfs/2.0")

$wfs.SelectNodes("//wfs:FeatureType", $ns) | ForEach-Object {
    [PSCustomObject]@{
        Name  = $_.Name
        Title = $_.Title
    }
} | Format-Table -AutoSize

#
# ZaplavUzemi_Q5          Zaplavova uzemi Q5
# ZaplavUzemi_Q20         Zaplavova uzemi Q20
# ZaplavUzemi_Q100        Zaplavova uzemi Q100
# ZaplavUzemi_Q500        Zaplavova uzemi Q500
# ZaplavUzemi_AktivniZony Zaplavova uzemi - aktivni zony Q100
# ZaplavUzemi_UsekyToku   Zaplavova uzemi - useky toku
#
# Q100 : flood discharge with an annual exceedance probability of 1% (often informally called a "100-year flood")
#        It does not mean such a flood happens exactly once every 100 years. 
# Q20  : 5% annual exceedance probability
# Q5   : 20% annual exceedance probability

# Inspecting the definition of FeatureType.

Invoke-WebRequest `
  -Uri "https://ags2.vuv.cz/arcgis/services/isvs_voda/isvs_voda/MapServer/WFSServer?service=WFS&version=2.0.0&request=DescribeFeatureType&typeNames=ZaplavUzemi_Q100" `
  -OutFile "q100-schema.xsd"

Get-Content .\q100-schema.xsd

# The most important field is:
#
# <xsd:element name="Shape"
#              nillable="true"
#              type="gml:MultiSurfacePropertyType"/>
#
# The flood zones are polygonal geometry (MultiSurface)

Invoke-WebRequest `
  -Uri "https://ags2.vuv.cz/arcgis/services/isvs_voda/isvs_voda/MapServer/WFSServer?service=WFS&version=2.0.0&request=GetFeature&typeNames=ZaplavUzemi_Q100&count=1" `
  -OutFile "q100-sample.xml"

Get-Item .\q100-sample.xml
Get-Content .\q100-sample.xml -TotalCount 50

# srsName="urn:ogc:def:crs:EPSG::5514" - that's EPSG:5514, S-JTSK / Krovak East North, the Czech projected coordinate system. 
# - a single Q100 feature can be a MultiSurface containing multiple polygons

# user-facing locations and OpenStreetMap data will normally be in EPSG:4326 (longitude/latitude), while this dataset is naturally EPSG:5514.

# Does the dataset eventually support EPSG:4326 (longitude/latitude)?

Invoke-WebRequest `
  -Uri "https://ags2.vuv.cz/arcgis/services/isvs_voda/isvs_voda/MapServer/WFSServer?service=WFS&version=2.0.0&request=GetFeature&typeNames=ZaplavUzemi_Q100&count=1&srsName=EPSG:4326" `
  -OutFile "q100-sample-4326.xml"

Select-String -Path .\q100-sample-4326.xml -Pattern 'srsName'

# native VÚV data
# EPSG:5514
#     |
#     | WFS srsName=EPSG:4326 ?
#     V
# longitude / latitude
# EPSG:4326

# EPSG:4326 is also supported
# srsName="urn:ogc:def:crs:EPSG::4326"
#
# VUV WFS can perform the CRS transformation server-side. 
# One subtle but important WFS/GML detail: in this EPSG:4326 response the coordinates are latitude, longitude, not longitude, latitude. That axis-order issue should be handled when constructing queries.
#
# This gives us two viable designs:
#
# A) VUV WFS --> EPSG:4326 --> application [easy win]
# B) VUV WFS --> EPSG:5514 --> GeoPandas/pyproj --> EPSG:4326 [PREFERRED IN THIS APPLICATION]
