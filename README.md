# Nutri-AI

A simple Streamlit application for calulating macros of food (...or other items) based on a picture.

## How it works?

1. User uploads a photo
2. The Olama "LLaVA" model is called to extract what foreground objects are exactly is in the photo + what are their weights. <br>The response is a JSON dictionary of item names and their weights.
3. The Ollama "Llama 3" model is called (with the response dictionary from the previous call passed as part of the prompt). <br>The task is to provide macros (Calories, Protein, Carbs, Fat) for the identified items. <br> Instead of asking the model to calulate the macros based on weights, it is asked to provide macros per 100g of a given identified item.
4. The JSON dict response is parsed and the total macros per weight are calulated. This approach proved much more robust, compared to asking the model to do the math by itself.
5. The calculated macros are saved as a Pandas dataframe. This enables easy usage of in-built Streamlit methods to show tables and charts + an easy CSV data download for the user.

## What is the architecture?

<TODO>