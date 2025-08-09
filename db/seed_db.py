import json
import psycopg2
import os

DB_URL = "dbname=ivf user=postgres password=pass host=localhost"

ROOT_DIR = os.path.dirname(os.path.dirname(__file__)) 
print(ROOT_DIR)

def seed(input_path):
    with open(input_path, "r") as f:
        data = json.load(f)

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    inserted = 0

    for c in data:
        if isinstance(c.get("cdc_success_rates"), dict):
            c["cdc_success_rates"] = json.dumps(c["cdc_success_rates"])
        if isinstance(c.get("national_cdc_success_rates"), dict):
            c["national_cdc_success_rates"] = json.dumps(c["national_cdc_success_rates"])
        
        cur.execute("""
            INSERT INTO clinics (
                name, number_of_doctors, avg_doctor_score, annual_cycles,
                national_annual_cycles, avg_rating, address, num_reviews,
                cdc_success_rates, avg_cdc_success_rate, national_cdc_success_rates,
                avg_national_cdc_success_rate, is_gaia_partner, city, state, zip_code,
                lat_city, lon_city, lat_state, lon_state, lat_zip, lon_zip,
                lat_city_state, lon_city_state, lat_city_state_zip, lon_city_state_zip,
                lat_address, lon_address, log_reviews, avg_cdc_success_rate_vs_national,
                annual_cycles_vs_national, norm_annual_cycles, norm_avg_cdc_success_rate,
                norm_avg_doctor_score, norm_avg_rating, norm_log_reviews
            ) VALUES (
                %(name)s, %(number_of_doctors)s, %(avg_doctor_score)s, %(annual_cycles)s,
                %(national_annual_cycles)s, %(avg_rating)s, %(address)s, %(num_reviews)s,
                %(cdc_success_rates)s, %(avg_cdc_success_rate)s, %(national_cdc_success_rates)s,
                %(avg_national_cdc_success_rate)s, %(is_gaia_partner)s, %(city)s, %(state)s, %(zip_code)s,
                %(lat_city)s, %(lon_city)s, %(lat_state)s, %(lon_state)s, %(lat_zip)s, %(lon_zip)s,
                %(lat_city_state)s, %(lon_city_state)s, %(lat_city_state_zip)s, %(lon_city_state_zip)s,
                %(lat_address)s, %(lon_address)s, %(log_reviews)s, %(avg_cdc_success_rate_vs_national)s,
                %(annual_cycles_vs_national)s, %(norm_annual_cycles)s, %(norm_avg_cdc_success_rate)s,
                %(norm_avg_doctor_score)s, %(norm_avg_rating)s, %(norm_log_reviews)s
            )
            ON CONFLICT (name, zip_code) DO NOTHING
        """, c)
    
        if cur.rowcount == 1:
            inserted += 1  

    conn.commit()
    cur.close()
    conn.close()
    print("Seeded", inserted, " clinics ")

if __name__ == "__main__":
    INPUT = os.path.join(ROOT_DIR, "data", "clinics_normalized.json")
    seed(INPUT)
