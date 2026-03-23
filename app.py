import streamlit as st
import requests
import base64
from PIL import Image
import io

# URL do Ollamy wewnątrz sieci Dockera
OLLAMA_URL = "http://ollama:11434/api/generate"


def analyze_image(image_bytes):
    # Model LLAVA do rozpoznania co jest na zdjęciu
    payload = {
        "model": "llava",
        "prompt": "What is in this image? Give me just the name of the object.",
        "stream": False,
        "images": [base64.b64encode(image_bytes).decode('utf-8')]
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response", "Unknown")


def get_macros(food_name):
    # Model LLAMA 3 do wyliczenia makro
    prompt = f"Provide nutritional macro values for {food_name}. If it's not food, try to estimate the nutritional."
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response", "No data")


# UI Streamlit
st.title("Vision + Macro AI")
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

if uploaded_file:
    img_bytes = uploaded_file.getvalue()
    st.image(img_bytes)

    if st.button("Analyze"):
        with st.spinner("Identifying..."):
            obj_name = analyze_image(img_bytes)
            st.write(f"Detected: {obj_name}")

        with st.spinner("Calculating macros..."):
            macros = get_macros(obj_name)
            st.info(macros)