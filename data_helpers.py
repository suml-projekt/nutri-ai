import json

def extract_and_parse_json(raw_text):
    """
    Scans a raw string from an LLM to find and extract a valid JSON dictionary.
    Returns a tuple: (parsed_dictionary, clean_json_string, error_message)
    """
    start_idx = raw_text.find('{')
    end_idx = raw_text.rfind('}') + 1
    
    if start_idx != -1 and end_idx != -1:
        clean_json_str = raw_text[start_idx:end_idx]
        try:
            # Try to convert the clean string into a Python dictionary
            parsed_dict = json.loads(clean_json_str)
            # Success! Return the dict, the string (for the next prompt), and None for the error.
            return parsed_dict, clean_json_str, None
        except json.JSONDecodeError as e:
            return None, None, f"Found brackets, but the JSON inside was invalid. Error: {e}"
    else:
        return None, None, "Could not find any JSON brackets '{ }' in the response."