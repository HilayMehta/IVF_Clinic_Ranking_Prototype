from fastapi.testclient import TestClient
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
sys.path.append(ROOT_DIR)

from src.main import app

client = TestClient(app)

def test_ranked_clinics_endpoint():
    resp = client.get("/get_ranked_clinics", params={"user_prompt": "We live in New York"})
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data


