# helpers.py
import json
import random
import time
import concurrent.futures
import streamlit as st
import requests
import base64
import pandas as pd

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
    
    if start_idx != -1 and end_idx != -1:       # if response contained a JSON-like structure:
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
        st.markdown(f"- **{str(item_name).title()}**: {weight}g")   # Add a capitalized item name + its weight for each entry

def analyze_image(image_bytes):
    """Analyzes the image by sending it to the Ollama API and returns the raw text response."""
    payload = {
        "model": "qwen2.5vl:3b",
        "prompt": get_vision_prompt(),
        "stream": False,
        "images": [base64.b64encode(image_bytes).decode('utf-8')],
        "options": {
            "temperature": 0.1,
            "num_ctx": 1024,
            "num_predict": 200
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response_data = response.json()
    if "error" in response_data:
        st.error(f"Ollama API Error: {response_data['error']}")
    return response_data.get("response", "{}")

def get_macros(json_data_string):
    """Sends the detected items and their weights to the Ollama API to get back estimated macros, then returns the raw text response."""
    payload = {
        "model": "qwen2.5vl:3b",
        "prompt": get_macro_prompt(json_data_string),
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 2048,
            "num_predict": 512
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response_data = response.json()
    
    if "error" in response_data:
        st.error(f"Ollama API Error: {response_data['error']}")
    return response_data.get("response", "{}")

def display_macros_and_totals(weights_dict, macro_dict):
    """Displays per-item macros and calculates/displays totals mathematically."""
    st.markdown("### 🥧 Nutritional Breakdown")
    
    records = []

    # Calculate actual macros for each item based on its weight and the 100g estimate
    for item, weight in weights_dict.items():
        macros_100g = macro_dict.get(item, {})
        
        factor = weight / 100.0
        cals = macros_100g.get("calories", 0) * factor
        protein = macros_100g.get("protein", 0) * factor
        carbs = macros_100g.get("carbs", 0) * factor
        fat = macros_100g.get("fat", 0) * factor

        records.append({
            "Item": str(item).title(),
            "Weight (g)": weight,
            "Calories": round(cals, 2),
            "Protein (g)": round(protein, 2),
            "Carbs (g)": round(carbs, 2),
            "Fat (g)": round(fat, 2)
        })
        
    df = pd.DataFrame(records)  # Create a DataFrame from the list of records for better Streamlit integration + data export
    
    # Display the dataframe directly to the user
    st.table(df)

    total_cals = df["Calories"].sum()
    total_protein = df["Protein (g)"].sum()
    total_carbs = df["Carbs (g)"].sum()
    total_fat = df["Fat (g)"].sum()

    # Render the calculated totals
    st.markdown("### Totals:")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])   # calories have more horizontal space
    
    c1.metric("Calories", f"{round(total_cals, 1)} kcal")
    c2.metric("Protein", f"{round(total_protein, 1)} g")
    c3.metric("Carbs", f"{round(total_carbs, 1)} g")
    c4.metric("Fat", f"{round(total_fat, 1)} g")

    # Pivot dataframe so Index = Macros, Columns = Items (required for the stacked bar view)
    chart_g_df = df.set_index("Item")[["Protein (g)", "Carbs (g)", "Fat (g)"]].T
    chart_kcal_df = df.set_index("Item")[["Calories"]].T

    st.bar_chart(chart_kcal_df, horizontal=True)  # Calories bar chart
    st.bar_chart(chart_g_df, horizontal=True)  # Macros bar chart
    
    # CSV Export Button
    st.markdown("### 💾 Export Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='nutrition_data.csv',
        mime='text/csv',
    )