import os
from dotenv import load_dotenv

import vertexai

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION")

client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

prompt = "You are a customer support assistant. Answer user questions about their orders."
output = client.prompts.optimize(prompt=prompt)

print(output.model_dump_json(indent=2))
