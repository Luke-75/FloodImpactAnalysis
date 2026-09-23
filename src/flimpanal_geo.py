# geo.py

from dotenv import load_dotenv
import os
from pathlib import Path

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
