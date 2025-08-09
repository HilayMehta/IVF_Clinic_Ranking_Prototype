# GAIA IVF Clinic Recommendation System

This is a prototype of IVF Clinic Recommendation System that helps users find the right fertility clinic for their IVF treatment using natural language input.

---

## Project Structure

```
GAIA/
├── data/                 # Raw and processed clinic datasets
├── db/                   # DB schema, seed and data loading logic script
├── src/
│   ├── data_pipeline/    # Scripts for crawling, scraping, cleaning & normalizing data
│   ├── utils/            # Helper functions
│   ├── ranking.py        # Ranking algorithm
│   ├── main.py           # FastAPI backend (API endpoints)
│   └── app.py            # Streamlit frontend
├── tests/                # Unit & integration tests
├── evals/                # Evaluation of user prompts
├── requirements.txt      # Project dependencies

```


---

## Setup Instructions

### 1. Clone the repository

```
git clone <repo_url>
cd <repo_name>
```

### 2. Create and activate a conda environment

```
conda create -name GAIA 
conda activate GAIA
conda install pip
pip install -r requirements.txt
python -m spacy download en_core_web_trf
```

### 3. Add Perplexity API key

Create a `.env` file in the project root and add:

```
PERPLEXITY_API_KEY = api_key
```
If you need the API key, feel free to reach out and I’d be happy to share it over email


---

## PostgreSQL Setup (macOS - Postgres App)

1. Install PostgreSQL 16 from the [official website](https://postgresapp.com/).

2. Verify installation and store the path (let's say: path_to_postgres):

```
ls -l /Applications/Postgres.app/Contents/Versions/16/bin/psql
```

3. Configure Postgres path in your conda environment:
Before proceeding, save the present directory path of your project
To get the path, run:

```
pwd
```
Copy the output path, which will be referred to as `conda_path`

Now run:

```
cd $CONDA_PREFIX
mkdir -p ./etc/conda/activate.d
cd ./etc/conda/activate.d
nano env_vars.sh
```

Paste the following:

```
#!/bin/sh
export PATH="path_to_postgres"
```
Replace `"path_to_postgres"` with the actual path to your PostgreSQL installation.  
For example, on macOS using Postgres.app, it might look like this:

```
#!/bin/sh
export PATH="/Applications/Postgres.app/Contents/Versions/16/bin:$PATH"
```

Save and exit:
- `Ctrl + O` → Enter
- `Ctrl + X`

Then make it executable and reload env:

```
chmod +x env_vars.sh
conda deactivate
conda activate GAIA
```

4. Verify:
Run the following to verify that the Postgres binary path is now correctly set in your environment:

```bash
cd conda_path
psql --version
```
Make sure to replace conda_path with the actual path you copied earlier

---

## Database Initialization

From the root project directory:

```
createdb ivf
psql -d ivf -f db/schema.sql
python db/seed_db.py  # Seeds the database
```

---

## Running the App

### First terminal: Backend API (FastAPI)

```
cd src
uvicorn main:app --reload
```
### Second terminal: Frontend (Streamlit)

In a separate terminal:

```
cd src
streamlit run app.py
```


---

## Running Integration & Unit Tests

```
cd tests
pytest -v
```

---

## Running Eval Script

```
cd evals
python eval_main.py
```

---
# Overall Approach, Design Choices, and Assumptions:

## Design Flow 

```

┌───────────────┐        ┌───────────┐              ┌────────────────────┐
│ Data Pipeline │   ───▶ │ Database  │  ─────▶      │ Ranking Algorithm  │
└───────────────┘        └───────────┘              └────────────────────┘
                                                               │
                                                               ▼
┌──────┐        ┌──────────────────────────┐       ┌──────────────────────────┐
│ Eval │  ◀───  │ Integration & Unit Tests │ ◀───  │    Frontend & Backend    │
└──────┘        └──────────────────────────┘       └──────────–───────────────┘                                                               
                                                                
    
```                                                          


---

# 1. Data Pipeline
src/data_pipeline

This component is responsible for **collecting, cleaning, and normalizing data** on real IVF clinics in the U.S.

---

### Data Source

Because **sartcorsonline.com** requires login access, I scraped data from **FertilityIQ**, which publicly lists ~100 fertility clinics across the U.S.

Each clinic record contained:

- **Clinic name**, **number of doctors**, and **average doctor score**  
- **Annual cycles** and **national average cycles**  
- **CDC success rates** vs. national averages for age groups: `<35`, `35–37`, `38–40`, `>40`  
- **Average rating** and **number of patient reviews**  
- **Address** (some clinics list multiple locations; the first address is used)  
- Clinic-level tags rating such as *LGBTQ+ friendly*, *operations quality*, etc.  


---

### Data Pipeline Steps

| Step | Script | Description |
|------|--------|-------------|
| 1 | `crawl.py` | Extracts URLs of ~100 clinics from the landing page |
| 2 | `scraping_clinics_links.py` | Visits each clinic page and extracts structured data |
| 3 | `add_gaia_flag_to_clinic.py` | Randomly assigns ~30 % of clinics as GAIA partners |
| 4 | `clean_clinics_data.py` | Removes or imputes data for clinics missing feature entries |
| 5 | `add_lat_long_to_clinics.py` | Extracts city/state/zip, then fetches latitude & longitude |
| 6 | `normalize_clinics_data.py` | Normalizes key metrics for downstream ranking |

---

### Feature Normalization Logic

Key features are normalized to enable fair comparisons:

| Feature | Normalization Method | Reason |
|---------|----------------------|--------|
| `log_reviews` | `log(num_reviews + 1)` then Min-Max scaling | Reduces skew from clinics with very high review counts then caps within [0,1] |
| `success_rate_vs_national` | `min(clinic / national, 1.0)` | Caps ratio within [0, 1] |
| `annual_cycles_vs_national` | `min(clinic / national, 1.0)` | Caps ratio within [0, 1] |
| `avg_doctor_score` | Min-Max scaling | Caps within [0, 1] |
| `success_rate` | Min-Max scaling | Caps within [0, 1] |
| `annual_cycles` | Min-Max scaling | Caps within [0, 1] |
| `avg_rating` | Min-Max scaling | Caps within [0, 1] |



---

### Assumptions & Design Choices

- **First address per clinic only** – for simplicity, we only pick the primary address where multiple branches are present for clinic.
- **Incomplete clinics removed** – records missing doctors or address are dropped during cleaning.  
- **GAIA partnership randomly assigned** – true GAIA affiliations are not public; ~30 % of clinics are flagged using a uniform random draw.  
- **Success rates averaged** – an overall `success_rate` is computed as the mean of age-group success rates for ranking purposes.  

---

Final Output file: `clinics_normalized.json`

---

# 2. Database 
src/db/

This component is responsible for database schema design, loading data into db 

---

**Database chosen:** **PostgreSQL**  

  Why?
  
  The dataset is highly structured with clear field relationships 
  Offers a native `JSONB` type &rightarrow; handy for fields such as `cdc_success_rates` and `national_cdc_success_rates`

---

### Files

| File            | Purpose                                                                   |
|-----------------|---------------------------------------------------------------------------|
| `schema.sql`    | Defines the PostgreSQL schema                                             |
| `seed_db.py`    | Loads the normalized clinic data into the DB                              |
| `db_loader.py`  | Helper functions to query data from PostgreSQL for ranking, API, etc.   |



### Schema Overview

| Column                                 | Type    | Notes / Usage                                           |
|----------------------------------------|---------|---------------------------------------------------------|
| `id`                                   | `SERIAL`| Primary key                                             |
| `name`, `zip_code`                     | `TEXT`  | Used as a **unique constraint** to prevent duplicate entries                         |
| `avg_doctor_score`                     | `FLOAT` | Mean doctor rating                                      |
| `annual_cycles`                        | `INT`   | Number of IVF cycles conducted                          |
| `success_rate`                         | `FLOAT` | Average success rate                                    |
| `lat_address`, `lon_address`, …        | `FLOAT` | Various geocodes used for ranking                       |
| `norm_*` fields                        | `FLOAT` | Min-max–scaled features for fair ranking                |
| `cdc_success_rates`, `national_cdc_success_rates` | `JSONB` | Optional analytics fields                               |


full DDL in `src/db/schema.sql`

---

# 3. Ranking Algorithm
src/ranking.py

This component identifies and ranks the top fertility clinics for a user based on **location** and **key features**.


---

### Part a) Candidate Selection 

- **Extract the city** from the user’s prompt. If a city is found, fetch its latitude and longitude; if no city is detected, politely return an error and ask the user to include a city
- Look for clinics in that city. If at least 4, rank and return them.
- If **fewer than 4 clinics** are available in that city, **expand to the entire state** so the recommendations are still nearby.  
- If there are **still fewer than 4 clinics**, we fall back to the **top clinics nationwide**. (This last step will likely be unnecessary once the dataset is larger.)


---

### Part b) Ranking Candidates

Each clinic from the candidate selection step above receives a score based on a weighted average of the features extracted and normalized.
The weights can be modified in the future, depending on the importance of the features, and can also be assigned dynamically based on user preference (if given in a prompt)
```
c["score"] = (
    0.1 * norm_annual_cycles +
    0.1 * annual_cycles_vs_national +
    0.1 * norm_success_rate +
    0.1 * success_rate_vs_national +
    0.1 * norm_avg_doctor_score +
    0.1 * norm_avg_rating +
    0.1 * norm_log_reviews +
    0.3 * distance_score      # Nearby clinics prioritized
)
```

Distance score calculations:

- Compare that to each clinic’s stored coordinates with the user's city coordinates extracted earlier.  
  *Because we only have the city (not the exact street address), the distance is an estimate—good enough to sort nearby options. In a future version, the system could ask the user for their ZIP code or full address, or even use the Google Maps API for more precise coordinates and distance calculation between coordinates (skipped here to avoid extra cost and rate limits).*

- We turn that distance into a score between **1** (right next door) and **0** (too far away) using a simple formula. DIST is decided upon if we are ranking clinics within the city (DIST = 50), state (DIST = 150), or the US (DIST = 500)

```text
distance_score = max(0, 1 - min(dist / DIST, 1))
```

In case of a tie in the score, the current system doesn't account for any ranking between them, but in the future we can give more priority to GAIA partners clinics or some features to break the tie.

---

# 4. Backend + Frontend
Backend: main.py
Frontend: streamlit_app.py

This component is responsible for the **frontend using Streamlit** and the **backend using FastAPI**

---

### Tech Stack 

| Layer / Purpose   | Technology           | 
|-------------------|----------------------|
| **API Endpoint**  | **FastAPI**          |
| **UI**            | **Streamlit**        | 
| **DB**            | **PostgreSQL**       |
| **LLM**           | **Perplexity API**   | 

 **Note:** Streamlit can be replaced with **React** for a more customized UI, and a different LLM can be plugged in easily depending on the use case or requirements.

- The user types something like *“We live in Seattle and are looking for top IVF clinics.”* in UI
- Streamlit issues a **GET** to `/get_ranked_clinics?user_prompt=...`.
- In Backend, retrieves clinics from PostgreSQL and calls `get_clinic_candidates_for_ranking` to rank clinics. Pass the prompt + ranked list to the Perplexity LLM. Return an LLM-generated summary as JSON
- UI displays the clinic's recommendation text, and if the clinic is a GAIA Partner, it is shown as a highlighted tag. For future versions, **clinic URLs as clickable links** can be included to help users quickly explore options and save time.


---

# 5. Integration & Unit Testing
tests/

This component **validates helper functions with unit tests** and **checks the full `/get_ranked_clinics` flow with an integration test**\

---
### Integration Test

Test verifies the `/get_ranked_clinics` FastAPI endpoint end-to-end and confirms:

- API is reachable
- Response JSON is in the expected format


### Unit Tests
Tests each helper function in isolation

- test_extract.py – verifies correct extraction of the city from a user prompt.
- test_geohelper.py – validates geo related helper functions such as get_distance, get_state_from_coords, etc

Haven't tested llm_helpers.py to avoid cost, and it is being evaluated in eval_main.py



---

# 6. Evaluation
evals/eval_main.py

This component runs sample user prompts through the full pipeline and shows the results

---

- Confirms the system handles edge cases (including typos, abbreviations, or missing cities)
- Manual evaluation for now, but can be automated later with benchmark tests or an “LLM-as-a-judge” setup

Note:
- The evaluation dataset is biased and not curated based on the original requests from users.
- Limited number of instances for now, can be scaled in the future.





