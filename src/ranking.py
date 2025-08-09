import json
import sys
import os



ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
sys.path.append(ROOT_DIR)

from src.utils.extract import extract_location
from src.utils.geo_helpers import get_lat_lon_fast, get_state_from_coords, distance_miles, get_state_abbr



def get_rank_clinics(clinics, user_coords, k=4, DIST = 200):
    ranked = []
    for c in clinics:
        # Address lat,long used as primary
        clinic_coords = None
        if c.get("lat_address") and c.get("lon_address"):
            clinic_coords = (c["lat_address"], c["lon_address"])
        elif c.get("lat_city_state_zip") and c["lon_city_state_zip"]:
            clinic_coords = (c["lat_city_state_zip"], c["lon_city_state_zip"])
        elif c.get("lat_zip") and c["lon_zip"]:
            clinic_coords = (c["lat_zip"], c["lon_zip"])
        elif c.get("lat_city_state") and c["lon_city_state"]:
            clinic_coords = (c["lat_city_state"], c["lon_city_state"])
        elif c.get("lat_city") and  c["lon_city"]:
            clinic_coords = (c["lat_city"], c["lon_city"])
        else:
            continue

        dist = distance_miles(user_coords, clinic_coords)
        c["distance_miles"] = dist
        c["norm_distance_score"] = max(0, 1 - min(dist / DIST, 1))

        c["score"] = (
            0.1 * c.get("norm_annual_cycles", 0) +
            0.1 * c.get("annual_cycles_vs_national", 0) +
            0.1 * c.get("norm_avg_cdc_success_rate", 0) +
            0.1 * c.get("avg_cdc_success_rate_vs_national", 0) +
            0.1 * c.get("norm_avg_doctor_score", 0) +
            0.1 * c.get("norm_avg_rating", 0) +
            0.1 * c.get("norm_log_reviews", 0) +
            0.3 * c.get("norm_distance_score", 0)
        )

        ranked.append(c)

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:k]

def get_clinic_candidates_for_ranking(user_prompt, clinics, k=4):

    user_city = extract_location(user_prompt)
    print(user_city)
    if not user_city:
        return {
            "error": "city not found in user prompt",
            "message": (
                "Sorry, we couldn’t detect a location in your message.\n"
                "Please include your city so that we can provide you with clinics nearby — for example:\n"
                "'We live in San Diego and are looking to start IVF treatment'"
            )
        }
    
    user_coords =  get_lat_lon_fast(user_city + ", USA")
    print(user_coords)
    
    if not user_coords:
        return {
            "error": "could not locate your city",
            "message": (
                "Sorry for the trouble but can you check if your location is correct in your message or try nearby popular city name.\n"
                "Please include your correct city so that we can provide you with clinics nearby — for example:\n"
                "'We live in San Diego and are looking to start IVF treatment'"
            )
        }
    

    ## City-level

    city_clinics = [c for c in clinics if c["city"].lower() == user_city.lower()]
    
    if len(city_clinics) >= k:
        return get_rank_clinics(city_clinics, user_coords, k, DIST = 50)

    
    ## State-level
    user_state = get_state_from_coords(user_coords)
    
    if not user_state:
        return {
            "error": "we could not locate the state in user prompt",
            "message": (
                "Sorry, we couldn’t detect your state in your message.\n"
                "Please include your correct city so that we can provide you with clinics nearby — for example:\n"
                "'We live in San Diego and are looking to start IVF treatment'"
            )
        }
   
    user_state_abbr = get_state_abbr(user_state)
    state_clinics = [c for c in clinics if c["state"].lower() == user_state_abbr.lower()]
    
    if len(state_clinics) >= k:
        return get_rank_clinics(state_clinics, user_coords, k, DIST = 150)
    
    
    # Country
    return get_rank_clinics(clinics, user_coords,k, DIST = 500)



if __name__ == "__main__":
    user_prompt = "We live in New York and are looking to start IVF soon."

    input_path = os.path.join(ROOT_DIR, "data", "clinics_normalized.json")

    with open(input_path, "r") as f:
        clinics = json.load(f)
    top_clinics = get_clinic_candidates_for_ranking(user_prompt, clinics, k=4)

    
