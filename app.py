# app.py
import streamlit as st
import requests
import base64

from prompts import get_vision_prompt, get_macro_prompt
# Import the two new lists along with our helpers
from data_helpers import (
    extract_and_parse_json, 
    run_with_dynamic_spinner, 
    VISION_MESSAGES, 
    MACRO_MESSAGES
)

OLLAMA_URL = "http://ollama:11434/api/generate"

def analyze_image(image_bytes):
    payload = {
        "model": "llava",
        "prompt": get_vision_prompt(),
        "stream": False,
        "images": [base64.b64encode(image_bytes).decode('utf-8')]
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response_data = response.json()
    if "error" in response_data:
        st.error(f"Ollama API Error: {response_data['error']}")
    return response_data.get("response", "{}")

def get_macros(json_data_string):
    payload = {
        "model": "llama3",
        "prompt": get_macro_prompt(json_data_string),
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response_data = response.json()
    if "error" in response_data:
        st.error(f"Ollama API Error: {response_data['error']}")
    return response_data.get("response", "No data")

# UI Streamlit
st.title("Vision + Macro AI")
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

if uploaded_file:
    img_bytes = uploaded_file.getvalue()
    st.image(img_bytes)

    if st.button("Analyze"):
        # Phase 1: Pass the VISION_MESSAGES list
        raw_response = run_with_dynamic_spinner(analyze_image, VISION_MESSAGES, img_bytes)
        parsed_dict, clean_json_str, error_msg = extract_and_parse_json(raw_response)

        if parsed_dict is not None:
            st.success("Detected Subjects & Weights:")
            st.json(parsed_dict)
            
            # Phase 2: Pass the MACRO_MESSAGES list
            macros = run_with_dynamic_spinner(get_macros, MACRO_MESSAGES, clean_json_str)
            st.info(macros)
            
        else:
            st.error(error_msg)
            st.write("Raw output from AI:")
            st.write(raw_response)