import os
import time
import requests
import streamlit as st

def initialize_ollama_models():
    if "models_initialized" not in st.session_state:
        st.session_state.models_initialized = False

    if st.session_state.models_initialized:
        return
        
    ollama_url = os.environ.get("LLM_URL", "http://localhost:11434")
    
    for _ in range(6):
        try:
            res = requests.get(f"{ollama_url}/api/tags")
            if res.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(5)
    else:
        st.error("Unable to reach Ollama container, check network configuration.")
        return

    try:
        existing_models = [m['name'] for m in res.json().get('models', [])]
        required_models = ["llava:latest", "llama3:latest"]
        
        for model in required_models:
            if model not in existing_models and f"{model}:latest" not in existing_models:
                with st.spinner(f"Initializing: Downloading {model}..."):
                    requests.post(f"{ollama_url}/api/pull", json={"name": model}, timeout=600)
        
        st.session_state.models_initialized = True
    except Exception as e:
        st.error(f"Error while initalizing models: {e}")