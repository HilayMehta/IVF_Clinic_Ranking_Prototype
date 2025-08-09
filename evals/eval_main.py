from fastapi.testclient import TestClient

import json
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__)) 
sys.path.append(ROOT_DIR)

from src.main import app

client = TestClient(app)

prompts = [
    "We live in New York and are looking for a IVF clinics",
    "Need IVF clinics in near San Diego",
    "We're in Texas and want clinics recommendations",
    "Looking for IVF clinics in Illinois",
    "What are the best fertility clinics near Los Angeles?",
    "Looking to start IVF treatment",
    "Looking to start treatment Settle", ## Incorrect spelling
    "Best IVF clinics in Bv" ## Bellevue city short form
]

results = []
for prompt in prompts:
    resp = client.get("/get_ranked_clinics", params={"user_prompt": prompt})
    if resp.status_code == 200:
        results.append({
            "prompt": prompt,
            "response": resp.json()
        })
    else:
        results.append({
            "prompt": prompt,
            "error": resp.status_code
        })
output_path = os.path.join(ROOT_DIR, "evals", "eval_results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
