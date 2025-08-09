
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
sys.path.append(ROOT_DIR)
from src.utils.geo_helpers import get_lat_lon_safe, get_state_from_coords, extract_location_from_address, distance_miles, get_state_abbr

def test_get_state_abbr():
    state = "New York"
    result = get_state_abbr(state)
    assert result.lower() == "ny"


def test_get_lat_lon_safe_valid():
    lat, lon = get_lat_lon_safe("New York")
    assert lat is not None
    assert lon is not None
    assert -90 <= lat <= 90
    assert -180 <= lon <= 180

def test_extract_location_from_address_valid():
    clinics = [{"address": "123 Main St, New York, NY 10001"}]
    result = extract_location_from_address(clinics)
    assert result[0]["city"] == "New York"


def test_get_state_from_coords():
    lat, lon = get_lat_lon_safe("New York")
    result = get_state_from_coords((lat, lon))
    assert result == "New York"

def test_distance_miles():
    coord1 = get_lat_lon_safe("New York")
    coord2 = get_lat_lon_safe("Los Angeles")
    result = distance_miles(coord1, coord2)
    assert 2400 < result < 2500
    