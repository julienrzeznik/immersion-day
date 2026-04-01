# Makefile for deploying the Service Health MCP server to Cloud Run

# Variables
ifeq ($(strip $(CENTRAL_HUB_PROJECT_ID)),)
$(error CENTRAL_HUB_PROJECT_ID is not set. Please set it to your GCP project ID)
endif
GCP_PROJECT_ID = $(CENTRAL_HUB_PROJECT_ID)
SERVICE_NAME ?= customers-mcp
REGION ?= europe-west1
IMAGE_NAME = gcr.io/$(GCP_PROJECT_ID)/$(SERVICE_NAME)

.PHONY: build deploy

dev:
	@uv run python mcp_server.py --transport http --port 8080

build:
	@uv pip compile pyproject.toml -o requirements.txt
	@echo "Building and pushing the Docker image to GCR..."
	gcloud builds submit --tag $(IMAGE_NAME) .

deploy: build
	@echo "Deploying the service to Cloud Run..."
	gcloud run deploy $(SERVICE_NAME) \
		--image $(IMAGE_NAME) \
		--project $(GCP_PROJECT_ID) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--service-account  central-mcp-sa@$(GCP_PROJECT_ID).iam.gserviceaccount.com

all: deploy
