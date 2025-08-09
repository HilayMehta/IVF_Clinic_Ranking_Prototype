import json
import re
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
sys.path.append(ROOT_DIR)

from src.utils.geo_helpers import get_lat_lon_safe, extract_location_from_address


def add_lat_lon_to_clinic(c):
    city, state, zip_code = c.get("city"), c.get("state"), c.get("zip_code")
    address = c.get("address")

    if city:
        c["lat_city"], c["lon_city"] = get_lat_lon_safe(city + ", USA")
    if state:
        c["lat_state"], c["lon_state"] = get_lat_lon_safe(state + ", USA")
    if zip_code:
        c["lat_zip"], c["lon_zip"] = get_lat_lon_safe(zip_code + ", USA")
    if city and state:
        c["lat_city_state"], c["lon_city_state"] = get_lat_lon_safe(city + ", " + state + ", USA")
    if city and state and zip_code:
        c["lat_city_state_zip"], c["lon_city_state_zip"] = get_lat_lon_safe(city + ", " + state + " " + zip_code + ", USA")
    if address:
        c["lat_address"], c["lon_address"] = get_lat_lon_safe(address + ", USA")
    # print("Fetched Lat and Long for City, State, Zip_Code")
    return c

def add_lat_lon_to_all_clinics(input_path, output_path):
    with open(input_path, "r") as f:
        clinics = json.load(f)
    clinics = extract_location_from_address(clinics)

    valid_clinics = []

    for c in clinics:
        c = add_lat_lon_to_clinic(c)

        coords = [c.get(k) for k in (
            "lat_city", "lon_city",
            "lat_state", "lon_state",
            "lat_zip", "lon_zip",
            "lat_city_state", "lon_city_state",
            "lat_city_state_zip", "lon_city_state_zip",
            "lat_address", "lon_address"
        )]

        has_any_coords = False
        for v in coords:
            if v is not None:
                has_any_coords = True
                break

        if has_any_coords:
            valid_clinics.append(c)
        else:
            print("Dropping clinic (no geocode found): ", c.get('name'))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(valid_clinics, f, indent=2)

    print(" Geocoding complete for clinics & saved to clinics_with_latlong.json")

if __name__ == "__main__":
    INPUT = os.path.join(ROOT_DIR, "data", "clinics_cleaned.json")
    OUTPUT = os.path.join(ROOT_DIR, "data", "clinics_with_latlong.json")
    add_lat_lon_to_all_clinics(INPUT, OUTPUT)
