# import json
# from geopy.geocoders import Nominatim
# from time import sleep

# INPUT_FILE = "clinics_GAIA.json"
# OUTPUT_FILE = "clinics_with_latlong.json"

# geolocator = Nominatim(user_agent="clinic_ranking")

# # ---- Helper: safe geocode with rate-limit handling ----
# def safe_geocode(query):
#     print("Executing Safe Geocode")
#     try:
#         loc = geolocator.geocode(query, country_codes="us", timeout = 10)
#         sleep(1)  # Respect Nominatim's 1 request/sec limit
#         if loc:
#             return loc.latitude, loc.longitude
#     except Exception as e:
#         print(f"❌ Geocode failed for {query}: {e}")
#     return None, None

# # ---- Load data ----
# with open(INPUT_FILE, "r") as f:
#     clinics = json.load(f)

# valid_clinics = []

# # ---- Generate lat/lon for different combinations ----
# for c in clinics:
#     city = c.get("city")
#     state = c.get("state")
#     zip_code = c.get("zip_code")

#     # 1️⃣ City only
#     if city:
#         c["lat_city"], c["lon_city"] = safe_geocode(f"{city}, USA")
#     else:
#         c["lat_city"], c["lon_city"] = None, None

#     # 2️⃣ State only
#     if state:
#         c["lat_state"], c["lon_state"] = safe_geocode(f"{state}, USA")
#     else:
#         c["lat_state"], c["lon_state"] = None, None

#     # 3️⃣ ZIP Code only
#     if zip_code:
#         c["lat_zip"], c["lon_zip"] = safe_geocode(f"{zip_code}, USA")
#     else:
#         c["lat_zip"], c["lon_zip"] = None, None

#     # 4️⃣ City + State
#     if city and state:
#         c["lat_city_state"], c["lon_city_state"] = safe_geocode(f"{city}, {state}, USA")
#     else:
#         c["lat_city_state"], c["lon_city_state"] = None, None

#     # 5️⃣ City + State + ZIP
#     if city and state and zip_code:
#         c["lat_city_state_zip"], c["lon_city_state_zip"] = safe_geocode(f"{city}, {state} {zip_code}, USA")
#     else:
#         c["lat_city_state_zip"], c["lon_city_state_zip"] = None, None

#     # ---- Check if ALL lat/lon are None ----
#     coords = [
#         c["lat_city"], c["lon_city"],
#         c["lat_state"], c["lon_state"],
#         c["lat_zip"], c["lon_zip"],
#         c["lat_city_state"], c["lon_city_state"],
#         c["lat_city_state_zip"], c["lon_city_state_zip"]
#     ]
#     if all(v is None for v in coords):
#         print(f"❌ Dropping clinic (no geocode found): {c.get('name')}")
#     else:
#         valid_clinics.append(c)

# # ---- Save updated dataset ----
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(valid_clinics, f, indent=2)

# print(f"✅ Geocoding complete. Saved to {OUTPUT_FILE}")
# print(f"✅ Dropped {len(clinics) - len(valid_clinics)} clinics with no coordinates")



from time import sleep
import re
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


geolocator = Nominatim(user_agent="clinic_ranking")

STATE_NAME_TO_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY"
}

def get_state_abbr(state_name):
    if not state_name:
        return None
    return STATE_NAME_TO_ABBR.get(state_name.lower())

def get_lat_lon_safe(query):
    print("Executing Safe Geocode")
    try:
        loc = geolocator.geocode(query, country_codes="us", timeout=10)
        sleep(1)  
        if loc:
            return loc.latitude, loc.longitude
    except Exception as e:
        print("Geocode failed for", query, ":", e)
    return None, None

def get_lat_lon_fast(query):
    print("Executing Safe Geocode")
    try:
        loc = geolocator.geocode(query, country_codes="us", timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception as e:
        print("Geocode failed for", query, ":", e)
    return None, None


def extract_location_from_address(clinics):
    """Extract city, state, zip_code from address using regex."""
    
    addr_pattern = re.compile(r",\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})")

    for clinic in clinics:
        address = clinic.get("address", "")
        match = addr_pattern.search(address)
        if match:
            clinic["city"] = match.group(1).strip()
            clinic["state"] = match.group(2).strip()
            clinic["zip_code"] = match.group(3).strip()
        else:
            clinic["city"] = None
            clinic["state"] = None
            clinic["zip_code"] = None
    print("Extracted City, State, Zip Code from Address")
    return clinics

def get_state_from_coords(coords):
    lat, lon = coords
    loc = geolocator.reverse((lat, lon), language="en")
    if loc and "address" in loc.raw:
        address = loc.raw["address"]
        return address.get("state")
    return None

def distance_miles(coord1, coord2):
    return geodesic(coord1, coord2).miles