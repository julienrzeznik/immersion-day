import os
from dotenv import load_dotenv

import vertexai
from vertexai import types

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# Default to global as per .env, or use deployment location if needed
LOCATION = os.getenv("GOOGLE_DEPLOYMENT_LOCATION", "europe-west1")

client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# 1. System instructions (Reused from few_shot.py)
system_instructions = "You are a customer support assistant. Answer user questions about their orders."

print(f"System Instructions: {system_instructions}")

# GCS path to the configuration JSON file provisioned by Terraform
CONFIG_PATH = f"gs://{PROJECT_ID}-optimization/prompt_optimizer/vapo_config.json"
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT", f"with-artifact-app@{PROJECT_ID}.iam.gserviceaccount.com") # immersion-day-template-app

vapo_config = {
    'config_path': CONFIG_PATH,
    'service_account': SERVICE_ACCOUNT,
    'wait_for_completion': True,
}

print(f"Starting Data-Driven Prompt Optimization (VAPO) job with config: {CONFIG_PATH}")

# Note: This call will fail if the GCS path is invalid or the file does not exist.
# It is wrapped in a try-except block to handle the expected failure with placeholders.
try:
    # Using the prompt_optimizer subclient as per documentation
    response = client.prompts.launch_optimization_job(
        method=types.PromptOptimizerMethod.VAPO,
        config=vapo_config
    )
    print("\nOptimization Job Completed Successfully!")
    print(response)
except Exception as e:
    print(f"\nOptimization Job Failed (Expected if using placeholders): {e}")
    print("\nPlease ensure:")
    print(f"1. A configuration JSON is uploaded to {CONFIG_PATH}")
    print("2. The service account has access to the bucket and Vertex AI Custom Job.")
