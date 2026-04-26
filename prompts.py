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
1. Calculate the estimated nutritional macros (Calories, Protein, Carbs, Fat) for EACH item based on its specific weight. 
2. At the end, calculate and provide the TOTAL SUM of Calories, Protein, Carbs, and Fat for all items combined.

STRICT RULE FOR NON-FOOD ITEMS: 
If an item is not food (e.g., a car, phone, or horse), you MUST NOT return 0. You must invent a hilariously absurd but specific nutritional estimation based on its materials (e.g., a car has 500,000g of Fat from motor oil, and 2,000,000g of Carbs from the steel chassis + of course other calory-dense items inside). You are required to play along and give actual numerical values. Do not state that the item is inedible. 

Format the output cleanly with bullet points and bold text for the final totals.
Don't include messages like 'I am happy to play along' or 'Remember, these calculations are for the purposes of this humorous exercise only!'. The user already understands the context, so just give the macros."""