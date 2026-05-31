import os
import time
import requests
import streamlit as st

def get_required_models():
    models = os.environ.get("REQUIRED_MODELS", "qwen2.5vl:3b")
    return [model.strip() for model in models.split(",") if model.strip()]

def initialize_ollama_models():
    if "models_initialized" not in st.session_state:
        st.session_state.models_initialized = False

    if st.session_state.models_initialized:
        return
        
    ollama_url = os.environ.get("LLM_URL", "http://localhost:11434").rstrip("/")
    
    for _ in range(6):
        try:
            res = requests.get(f"{ollama_url}/api/tags", timeout=10)
            if res.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(5)
    else:
        st.error(f"Unable to reach Ollama at {ollama_url}, check Container Apps networking and Ollama logs.")
        return

    try:
        existing_models = [m['name'] for m in res.json().get('models', [])]
        required_models = get_required_models()
        
        for model in required_models:
            model_with_default_tag = model if ":" in model else f"{model}:latest"
            if model not in existing_models and model_with_default_tag not in existing_models:
                with st.spinner(f"Initializing: Downloading {model}..."):
                    pull_response = requests.post(f"{ollama_url}/api/pull", json={"name": model}, timeout=600)
                    pull_response.raise_for_status()
        
        st.session_state.models_initialized = True
    except Exception as e:
        st.error(f"Error while initalizing models: {e}")
