from src.flimpanal_geo import geocode

lat, lon = geocode("Prague")
print(f"Latitude: {lat}, Longitude: {lon}")
