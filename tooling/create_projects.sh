#!/bin/bash

# Ensure the script exits on errors
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <index>"
  echo "Example: $0 001"
  exit 1
fi

INDEX=$1

FOLDER_ID="XXX"
BILLING_ACCOUNT="XXX-YYYYY-ZZZZZZ"

PREFIXES=(
  "immersion-day-central-hub"
  "immersion-day-sandbox"
  "immersion-day-staging"
  "immersion-day-prod"
)

echo "Starting project creation for index: ${INDEX} in folder: ${FOLDER_ID}..."

for PREFIX in "${PREFIXES[@]}"; do
  PROJECT_ID="${PREFIX}-${INDEX}"
  
  echo "------------------------------------------------------------"
  echo "Creating Project: ${PROJECT_ID}..."
  
  # Create the project inside the specified folder
  # We ignore failures (|| true) in case the project already exists to let the script keep running, 
  # or you can remove '|| true' to make it fail fast if a project creation fails.
  gcloud projects create "${PROJECT_ID}" --folder="${FOLDER_ID}" --name="${PROJECT_ID}"
  
  echo "Linking Billing Account: ${BILLING_ACCOUNT} to ${PROJECT_ID}..."
  gcloud beta billing projects link "${PROJECT_ID}" --billing-account="${BILLING_ACCOUNT}"
  
  echo "Successfully created and linked billing for: ${PROJECT_ID}"
done

echo "------------------------------------------------------------"
echo "All done! 4 projects created and linked to billing."
