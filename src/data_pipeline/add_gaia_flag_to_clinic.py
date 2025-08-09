import json
import os
import random
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  

def assign_random_gaia_flags(input_path, output_path, probability=0.3):
    with open(input_path, "r") as f:
        clinics = json.load(f)
    for clinic in clinics:
        clinic["is_gaia_partner"] = random.random() < probability
    with open(output_path, "w") as f:
        json.dump(clinics, f, indent=2)

if __name__ == "__main__":
    INPUT = os.path.join(ROOT_DIR, "data", "clinics_scrapped.json")
    OUTPUT = os.path.join(ROOT_DIR, "data", "clinics_with_gaia.json")
    assign_random_gaia_flags(INPUT, OUTPUT, 0.3)