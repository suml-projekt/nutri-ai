# app.py
import streamlit as st
import io
from PIL import Image

from constants import VISION_MESSAGES, MACRO_MESSAGES
from utils import initialize_ollama_models

from helpers import (
    run_with_dynamic_spinner, 
    extract_and_parse_json, 
    get_macros, 
    display_detected_items, 
    analyze_image, 
    display_macros_and_totals
)

initialize_ollama_models()

if st.session_state.get("models_initialized", False):

    # UI Streamlit
    st.title("🥗 Nutri-AI")
    st.markdown("""**:rainbow[Your best nutrition AI buddy] - analyze your food ...or maybe your car!? Nutri-AI can do it all!**""")
    st.divider()

    uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file);
        if img.mode in ("RGBA", "P"):
            img = img.convert("RBG")
        img.thumbnail((512, 512))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()
        st.image(img_bytes)

        if st.button("Analyze"):
            # Phase 1: Image analysis:
            raw_vision_response = run_with_dynamic_spinner(analyze_image, VISION_MESSAGES, img_bytes)
            parsed_weights_dict, clean_weights_json_str, vision_error = extract_and_parse_json(raw_vision_response)

            if parsed_weights_dict is not None:
                st.success("Image successfully analyzed!")
                display_detected_items(parsed_weights_dict)
                st.divider() 
            
                # Phase 2: Getting macros / 100g + calculation totals for items based on their weights:
                raw_macro_response = run_with_dynamic_spinner(get_macros, MACRO_MESSAGES, clean_weights_json_str)
                parsed_macros_dict, clean_macros_json_str, macro_error = extract_and_parse_json(raw_macro_response)
            
                if parsed_macros_dict is not None:
                    st.success("Macros calculated successfully!")
                    st.balloons()
                    display_macros_and_totals(parsed_weights_dict, parsed_macros_dict)  # Display info in a nice formatted way, including totals and charts
                else:
                    st.error(macro_error)
                    st.write("Raw output from AI:")
                    st.write(raw_macro_response)
            
            else:
                st.error(vision_error)
                st.write("Raw output from AI:")
                st.write(raw_vision_response)

else:
    st.warning("Waiting for the models...")