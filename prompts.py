def get_vision_prompt():
    """Returns the strict JSON prompt for the Llava vision model."""
    return """Analyze this image and identify ONLY the main subjects (e.g., specific food items on a plate, a main animal). 
Ignore containers (like plates, bowls, cups) and background objects (tables, stables, scenery). 
Estimate the weight of each identified main subject in grams. 

You MUST return the result strictly as a valid JSON dictionary where the keys are the object names (strings) and the values are the estimated weights in grams (integers). 
Do NOT include any markdown formatting like ```json. Do NOT include any introductory or concluding text. Return ONLY the raw JSON object.

Remember, if identifying a big object (like a horse, house or a car), provide a reasonable weight estimate in grams (e.g., 450000 grams for a horse).

Examples:
- A plate with chicken, potatoes, and salad: {"chicken": 150, "potatoes": 200, "salad": 100}
- A horse standing in a stable: {"horse": 450000}
- A car {"porsche": 1500000}
"""

def get_macro_prompt(json_data_string):
    """Takes the JSON string of weights and returns the prompt for Llama3."""
    return f"""I am providing a JSON dictionary containing items and their estimated weights in grams:
{json_data_string}

Task:
Provide the estimated nutritional macros (Calories, Protein, Carbs, Fat) PER 100 GRAMS for EACH item based on its name. 

You MUST return the result strictly as a valid JSON dictionary where the keys are the object names and the values are dictionaries containing the numerical macros per 100g. 
Do NOT include any markdown formatting like ```json. Do NOT include any introductory or concluding text. Return ONLY the raw JSON object. Do NOT calculate the totals based on the provided weights. Only provide the per 100g values.

CRITICAL JSON RULE:
Return ONLY the final numerical values per 100g. Do NOT return mathematical equations or formulas inside the JSON values.

STRICT RULE FOR NON-FOOD ITEMS: 
If an item is not food (e.g., a car, phone, or horse), you MUST NOT return 0. You must invent a hilariously absurd but specific nutritional estimation per 100g based on its materials.
The user already understands the context of the items, so there is no need to explain or justify your estimates. Just provide the numbers.

Expected JSON format exactly like this:
{{
  "chicken": {{"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6}},
  "potatoes": {{"calories": 77, "protein": 2, "carbs": 17, "fat": 0.1}}
}}
or:
{{
  "honda civic": {{"calories": 1000, "protein": 0, "carbs": 30, "fat": 80}}
}}
"""