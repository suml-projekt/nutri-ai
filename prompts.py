def get_vision_prompt():
    """Returns the strict JSON prompt for the Llava vision model."""
    return """Analyze the image. List every distinct food item you can see.
For each food item, estimate its weight in grams based on typical serving sizes.

Rules:
- Ignore plates, bowls, cups, cutlery, and background
- If unsure about a food item, make your best guess
- Use simple, common names (e.g. "chicken" not "grilled chicken breast")

Return ONLY a JSON object, no other text, no markdown, no explanation.

Examples:
Input: plate with chicken, potatoes, salad
Output: {"chicken": 150, "potatoes": 200, "salad": 100}

Input: orange on a table  
Output: {"orange": 180}

Input: bowl of pasta with tomato sauce
Output: {"pasta": 250, "tomato sauce": 80}

Now analyze the image and return the JSON:"""

def get_macro_prompt(json_data_string):
    """Takes the JSON string of weights and returns the prompt for Llama3."""
    return """You are a nutrition database. Return macros per 100g for each provided food item.
              Output format - ONLY this JSON, nothing else:
{
  "item_name": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
  "item_name2": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
}

Rules:
- Values are per 100g, integers or one decimal place floats
- No markdown, no explanation, no text before or after the JSON
- For non-food items: invent absurd but specific numbers (e.g. car engine oil: high fat, zero protein)
""" + f"""
Items to analyze:
{json_data_string}"""