import os
import requests
import textwrap
from fastapi import HTTPException


from dotenv import load_dotenv
load_dotenv()

def get_clinics_recommendations_from_llm(user_prompt: str, ranked_clinics, model: str = "sonar") -> str:
    system_msg = "You are a helpful fertility-clinic advisor."
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY not found")
    user_msg = textwrap.dedent(f"""
    Based on the user query, I will provide you with ranked clinics and their details. 
    I want you to give clinics name in numbered bullet points format based on the ranking provided as well as write a short description for each of the clinics using the detail. 
    
    I am providing you an example below:
    ---
    User query: We are a heterosexual couple. We live in New York. We are looking to start IVF treatment next month. Which fertility clinics should we consider?
    
    Output: 
        For heterosexual couples seeking IVF treatment in New York, there are several reputable fertility clinics to consider:
        1. New Hope Fertility Center: Located in NYC, this clinic specializes in minimally invasive IVF treatments and boasts success rates of 58%, compared to the national average of 43%. They offer personalized care and a range of treatment options.

        2. Kofinas Fertility Group: Rated as one of the best fertility clinics in New York by several publications, Kofinas Fertility Group has five convenient locations across the New York metro area. They provide comprehensive fertility services and have a strong track record of success.

        3. Chelsea Fertility NYC **GAIA PARTNER**: This internationally recognized fertility center offers a full spectrum of care, including IVF, and is known for its personalized approach. Their doctors are experienced IVF pioneers.

        4. New York City IVF: This clinic combines scientific and holistic care to improve success rates. They offer modern, personalized fertility care in a private and compassionate setting, with all facilities in-house.

        When choosing a clinic, consider factors such as success rates, treatment options, cost, and the level of personalized care offered. It’s recommended to schedule consultations with multiple clinics to find the best fit for your specific needs and preferences.
    


    Now, respond to the following user query in the same style, tone, and formatting. 
    # If any clinic in the ranked list has `"is_gaia_partner": true`, add **GAIA PARTNER** in bold after its name (exactly as in the example) and make sure not to repeat it any where else in clinic description.

    For the User query: "{user_prompt}" respond based on the Ranked Clinic Data: {ranked_clinics}. If there is some error message in Ranked Clinic Data, then politely respond to user with the error message and ask user to correct it
    
    End with: "When choosing a clinic, consider factors such as success rates, treatment options, cost, and the level of personalized care offered. It’s recommended to schedule consultations with multiple clinics to find the best fit for your specific needs and preferences." if there was no error message
    """)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg}
        ]
    }
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Perplexity API failed: {str(e)}")


