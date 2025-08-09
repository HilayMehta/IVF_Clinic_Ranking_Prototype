import streamlit as st
import requests, re

API_URL = "http://127.0.0.1:8000/get_ranked_clinics"  


if "view" not in st.session_state:
    st.session_state.view = "input"
if "recommendations" not in st.session_state:
    st.session_state.recommendations = ""

## First Screen
if st.session_state.view == "input":
    st.title("Fertility Clinic Advisor")

    user_prompt = st.text_area(
        "We can help you find the right fertility clinic for your IVF treatment. Tell us about your IVF treatment requirements and what is important for you",
        placeholder="Example: We live in New York and are looking to start IVF next month. Which fertility clinics should we consider?"
    )

    if st.button("Find Clinics"):
        if not user_prompt.strip():
            st.error("Please enter your requirements")
        else:
            with st.spinner("Fetching clinics recommendations..."):
                try:
                    resp = requests.get(API_URL, params={"user_prompt": user_prompt}, timeout=60)
                    resp.raise_for_status()
                    data = resp.json()
                    if isinstance(data, dict) and "recommendations" in data:
                        st.session_state.recommendations = data["recommendations"]
                        st.session_state.user_prompt = user_prompt 
                        st.session_state.view = "results"
                        st.rerun()
                    else:
                        st.error("Unexpected API response format.")
                except requests.exceptions.RequestException as e:
                    st.error("Error contacting API: " + str(e))

## Second Screen
elif st.session_state.view == "results":
    st.title(st.session_state.user_prompt)
    
    ## GAIA Partner
    highlighted = st.session_state.recommendations.replace(
        "**GAIA PARTNER**",
        '<span style="background-color: yellow; color: black; font-weight: bold;">GAIA PARTNER</span>'
    )

    st.markdown(highlighted, unsafe_allow_html=True)


    

    if st.button(" Back to Search"):
        st.session_state.view = "input"
        st.rerun()
