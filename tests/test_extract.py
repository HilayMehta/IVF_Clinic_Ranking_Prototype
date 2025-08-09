
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
sys.path.append(ROOT_DIR)
from src.utils.extract import extract_location

def test_extract_location():
    prompt = "I live in Seattle"
    result = extract_location(prompt)
    assert result == "Seattle"
    