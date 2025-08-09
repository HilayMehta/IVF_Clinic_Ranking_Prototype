import json
import math
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  


def preprocess_scores(clinics):
    for c in clinics:
        c["log_reviews"] = math.log(c.get("num_reviews", 0) + 1)

        c["avg_cdc_success_rate_vs_national"] = min(
            c["avg_cdc_success_rate"] / c["avg_national_cdc_success_rate"], 1.0
        )

        c["annual_cycles_vs_national"] = min(
            c["annual_cycles"] / c["national_annual_cycles"], 1.0
        )
    return clinics


def minmax(values):
    lo, hi = min(values), max(values)
    return lo, hi if hi > lo else (lo, lo + 1e-6)


def normalize_fields(clinics, keys_to_norm):
    mins, maxs = {}, {}
    for key in keys_to_norm:
        vals = [c[key] for c in clinics if c[key] is not None]
        mins[key], maxs[key] = minmax(vals)

    for c in clinics:
        for key in keys_to_norm:
            lo, hi = mins[key], maxs[key]
            c["norm_" + key] = (c[key] - lo) / (hi - lo)

    return clinics


def normalize_clinics(input_path, output_path):
    with open(input_path, "r") as f:
        clinics = json.load(f)

    clinics = preprocess_scores(clinics)

    keys_to_norm = [
        "annual_cycles", "avg_cdc_success_rate", "avg_doctor_score", "avg_rating", "log_reviews"
    ]

    clinics = normalize_fields(clinics, keys_to_norm)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clinics, f, indent=2)

    print("Normalized data saved to clinics_normalized.json")


if __name__ == "__main__":
    INPUT_FILE = os.path.join(ROOT_DIR, "data", "clinics_with_latlong.json")
    OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "clinics_normalized.json")
    normalize_clinics(INPUT_FILE, OUTPUT_FILE)
