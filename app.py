import streamlit as st
import requests
import base64

# Import your helper functions
from prompts import get_vision_prompt, get_macro_prompt
from data_helpers import extract_and_parse_json

# URL do Ollamy wewnątrz sieci Dockera
OLLAMA_URL = "http://ollama:11434/api/generate"

def analyze_image(image_bytes):
    payload = {
        "model": "llava",
        "prompt": get_vision_prompt(),
        "stream": False,
        "images": [base64.b64encode(image_bytes).decode('utf-8')]
    }
    response = requests.post(OLLAMA_URL, json=payload)
    
    # Catch Ollama API errors
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
    
    # Catch Ollama API errors
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
        with st.spinner("Identifying and estimating weights..."):
            raw_response = analyze_image(img_bytes)
            
            # Use the new helper function to clean and parse the data
            parsed_dict, clean_json_str, error_msg = extract_and_parse_json(raw_response)
            
            # If the parser successfully returned a dictionary, proceed
            if parsed_dict is not None:
                st.success("Detected Subjects & Weights:")
                st.json(parsed_dict)
                
                with st.spinner("Calculating macros and totals..."):
                    # Pass the clean string (not the dictionary!) to the next prompt
                    macros = get_macros(clean_json_str)
                    st.info(macros)
            
            # If the parser failed, show the exact error and the raw AI text
            else:
                st.error(error_msg)
                st.write("Raw output from AI:")
                st.write(raw_response)