import json
import os
import statistics

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  


def drop_missing_critical_fields(clinics):

    Fields = ["name", "address", "url"]
    before = len(clinics)
    filtered = [
        c for c in clinics
        if all(c.get(field) not in (None, "") for field in Fields)
    ]
    dropped = before - len(filtered)
    print( "Clinics with missing critical fields:", dropped )
    return filtered


def fill_defaults(clinics, Avg_National_Cdc_Success_Rate = 0.4395, Avg_National_Annual_Cycles = 738):

    for c in clinics:
        if c.get("avg_national_cdc_success_rate") is None:
            c["avg_national_cdc_success_rate"] = Avg_National_Cdc_Success_Rate
        if c.get("national_annual_cycles") is None:
            c["national_annual_cycles"] = Avg_National_Annual_Cycles
    return clinics


def fill_missing_annual_cycles(clinics):
    annual_vals = [c["annual_cycles"] for c in clinics if c["annual_cycles"] is not None]
    median_cycles = statistics.median(annual_vals) if annual_vals else 0

    for c in clinics:
        if c["annual_cycles"] is None:
            c["annual_cycles"] = median_cycles

    
    return clinics


def fill_missing_avg_cdc_success_rates(clinics, Avg_National_Cdc_Success_Rate = 0.4395):
    for c in clinics:
        if c["avg_cdc_success_rate"] is None:
            c["avg_cdc_success_rate"] = c.get("avg_national_cdc_success_rate", Avg_National_Cdc_Success_Rate)
    return clinics


def clean_clinic_data(input_path, output_path):
    with open(input_path, "r") as f:
        clinics = json.load(f)

    clinics = drop_missing_critical_fields(clinics)
    clinics = fill_defaults(clinics, 0.4395, 738)
    clinics = fill_missing_annual_cycles(clinics)
    clinics = fill_missing_avg_cdc_success_rates(clinics, 0.4395)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clinics, f, indent=2)

    print("Cleaned data saved to cleaned_clinics.json")


if __name__ == "__main__":
    INPUT_FILE = os.path.join(ROOT_DIR, "data", "clinics_with_gaia.json")
    OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "clinics_cleaned.json")
    clean_clinic_data(INPUT_FILE, OUTPUT_FILE)
