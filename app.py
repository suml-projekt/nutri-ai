# app.py
import streamlit as st

from constants import VISION_MESSAGES, MACRO_MESSAGES

from helpers import (
    run_with_dynamic_spinner, 
    extract_and_parse_json, 
    get_macros, 
    display_detected_items, 
    analyze_image, 
    display_macros_and_totals
)

# UI Streamlit
st.title("🥗 Nutri-AI")
st.markdown("""**:rainbow[Your best nutrition AI buddy] - analyze your food ...or maybe your car!? Nutri-AI can do it all!**""")
st.divider()

uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

if uploaded_file:
    img_bytes = uploaded_file.getvalue()
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