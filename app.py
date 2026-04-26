# app.py
import streamlit as st

from constants import VISION_MESSAGES, MACRO_MESSAGES
from helpers import run_with_dynamic_spinner, extract_and_parse_json, get_macros, display_detected_items, analyze_image

# UI Streamlit
st.title("🥗 Nutri-AI")
st.markdown("""**:rainbow[Your best nutrition AI buddy] - analyze your food ...or maybe your car!? Nutri-AI can do it all!**""")

uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

if uploaded_file:
    img_bytes = uploaded_file.getvalue()
    st.image(img_bytes)

    if st.button("Analyze"):
        # Phase 1: Vision
        raw_response = run_with_dynamic_spinner(analyze_image, VISION_MESSAGES, img_bytes)
        parsed_dict, clean_json_str, error_msg = extract_and_parse_json(raw_response)

        if parsed_dict is not None:
            st.success("Image successfully analyzed!")
            display_detected_items(parsed_dict)
            st.divider() 
            
            # Phase 2: Macros
            # Unpack the new tuple we created in get_macros
            macros_text, macro_error = run_with_dynamic_spinner(get_macros, MACRO_MESSAGES, clean_json_str)
            
            if macros_text is not None:
                # Green success message
                st.success("Macros calculated successfully!")
                st.balloons()
                # Normal text on normal background
                st.markdown(macros_text)
            else:
                # Red error message
                st.error(macro_error)
            
        else:
            st.error(error_msg)
            st.write("Raw output from AI:")
            st.write(raw_response)