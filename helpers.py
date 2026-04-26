# data_helpers.py
import json
import random
import time
import concurrent.futures
import streamlit as st
import requests
import base64

from constants import OLLAMA_URL
from prompts import get_vision_prompt, get_macro_prompt

def run_with_dynamic_spinner(func, message_list, *args):
    """
    Runs a function in a background thread and cycles through 
    a provided list of loading messages until it finishes.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        
        status_text = st.empty()
        
        while not future.done():
            msg = random.choice(message_list)
            status_text.markdown(f"**⏳ {msg}**")
            time.sleep(3)
            
        status_text.empty() # Clear the message when finished
        return future.result()

def extract_and_parse_json(raw_text):
    """
    Scans a raw string from an LLM to find and extract a valid JSON dictionary.
    """
    start_idx = raw_text.find('{')
    end_idx = raw_text.rfind('}') + 1
    
    if start_idx != -1 and end_idx != -1:
        clean_json_str = raw_text[start_idx:end_idx]
        try:
            parsed_dict = json.loads(clean_json_str)
            return parsed_dict, json.dumps(parsed_dict), None
        except json.JSONDecodeError as e:
            return None, None, f"JSON invalid. Error: {e}"
    else:
        return None, None, "No JSON brackets found."
    
def display_detected_items(weights_dict):
    """Takes the parsed JSON dictionary and formats it as a clean Streamlit list."""
    st.markdown("### 🔍 Detected Subjects")
    for item_name, weight in weights_dict.items():
        # .title() capitalizes the first letter of each word (e.g., "hot dog" -> "Hot Dog")
        st.markdown(f"- **{str(item_name).title()}**: {weight}g")

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
    
    # Return a tuple (data, error) to perfectly match Phase 1's logic
    if "error" in response_data:
        return None, f"Ollama API Error: {response_data['error']}"
        
    return response_data.get("response", "No data"), None