import os
from dotenv import load_dotenv

import pandas as pd

import vertexai
from vertexai import types

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION")

client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

system_instructions = "You are a customer support assistant. Answer user questions about their orders."
df = pd.DataFrame(
    [
        {
            "prompt": "I just opened my package and the coffee machine I ordered is completely smashed. The glass carafe is everywhere. What should I do?",
            "model_response": "You need to return the item to get a refund or a replacement.",
            "rubrics": "['Shows empathy', 'Actionable steps']",
            "rubrics_evaluations": "[False, False]",
        },
        {
            "prompt": "I'm trying to buy a gift for my sister in London. Do you guys ship internationally, and how long does it usually take?",
            "model_response": "Yes, we ship internationally. Shipping times vary by country",
            "rubrics": "['Shows empathy', 'Actionable steps']",
            "rubrics_evaluations": "[False, False]",
        },
    ]
)

config = vertexai.types.OptimizeConfig(
    optimization_target=vertexai.types.OptimizeTarget.OPTIMIZATION_TARGET_FEW_SHOT_RUBRICS,
    examples_dataframe=df,
)

response = client.prompts.optimize(prompt=system_instructions, config=config)

print(response.parsed_response.suggested_prompt)
