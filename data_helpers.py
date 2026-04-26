# data_helpers.py
import json
import random
import time
import concurrent.futures
import streamlit as st

# Messages for the Image Recognition Phase
VISION_MESSAGES = [
    "Counting the pixels in your lunch...",
    "Teaching the AI the difference between a car and a taco...",
    "Checking if that's a potato or a rock...",
    "Squinting really hard at the image...",
    "Translating shapes into dinner...",
    "Asking the neural network what's on the menu...",
    "Scanning for hidden vegetables...",
    "Determining if it's a hotdog or not a hotdog...",
    "Deploying tiny digital chefs to inspect the plate...",
    "Estimating gravity's effect on this portion size..."
]

# Messages for the Math & Nutrition Phase
MACRO_MESSAGES = [
    "Consulting the digital oracle...",
    "Calculating macros. This might take a byte...",
    "Converting grams into high-protein data...",
    "Adjusting the calorie-o-meter...",
    "Summoning the spirits of nutritionists past...",
    "Crunching the numbers (and the carbs)...",
    "Doing the math so you don't have to...",
    "Cross-referencing with the database of all known foods...",
    "Dividing by zero... wait, no, just calculating fats...",
    "Extracting the digital vitamins..."
]

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