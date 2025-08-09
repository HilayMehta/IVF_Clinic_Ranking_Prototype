from fastapi import FastAPI
import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)  
from db.db_loader import load_all_clinics
from src.ranking import get_clinic_candidates_for_ranking
from src.utils.llm_helpers import get_clinics_recommendations_from_llm



app = FastAPI()

@app.get("/get_ranked_clinics")
def ranked_clinics(user_prompt: str, k: int = 4, DIST: int = 200):
    print("This is working")
    clinics = load_all_clinics()
    ranked_clinics = get_clinic_candidates_for_ranking(user_prompt, clinics, k)

    recommendations = get_clinics_recommendations_from_llm(user_prompt, ranked_clinics, model = "sonar")
    return {"recommendations": recommendations}
