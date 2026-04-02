
# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# Rename the project prefix to prevent collisions
# Usage: make rename PREFIX=myprefix
rename:
	@if [ -z "$(PREFIX)" ]; then echo "Error: PREFIX is not set. Usage: make rename PREFIX=myprefix"; exit 1; fi
	@uv run python scripts/rename_template.py "$(PREFIX)"

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

playground-memory-bank:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	AGENT_ENGINE_URL=$$(jq -r .remote_agent_engine_id deployment_metadata.json) && \
	uv run adk web . --port 8501 --reload_agents --memory_service_uri="agentengine://$$AGENT_ENGINE_URL"

playground-a2a:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your A2A Hello World agent...                                   |"
	@echo "|                                                                             |"
	@echo "| 📡 Listening on http://localhost:8001                                       |"
	@echo "|                                                                             |"
	@echo "==============================================================================="
	uv run uvicorn app.a2a.a2a_agent:a2a_app --host localhost --port 8001 --reload

mcp-inspector:
	@echo "==============================================================================="
	@echo "| 🔍 Starting MCP Inspector...                                                |"
	@echo "| Select SSE and use the agent's URL if supporting SSE over MCP.              |"
	@echo "==============================================================================="
	npx -y @modelcontextprotocol/inspector
	
a2a-inspector:
	@echo "==============================================================================="
	@echo "| 🕵️  Setting up and running A2A Inspector...                               |"
	@echo "|                                                                             |"
	@echo "| This will clone the A2A Inspector locally if it doesn't exist and run it.   |"
	@echo "==============================================================================="
	@if [ ! -d ".a2a-inspector" ]; then \
		git clone https://github.com/a2aproject/a2a-inspector.git .a2a-inspector; \
		cd .a2a-inspector && uv sync && cd frontend && npm install; \
	fi
	@cd .a2a-inspector && bash scripts/run.sh

# ==============================================================================
# Prompt Optimization
# ==============================================================================

# Run prompt optimization
# Usage: make optimize-prompt TYPE=zero_shot|few_shot|data_driven
optimize-prompt:
	@if [ -z "$(TYPE)" ]; then echo "Error: TYPE is not set. Usage: make optimize-prompt TYPE=zero_shot"; exit 1; fi
	uv run app/optimization/prompt_optimization/$(TYPE).py

# ==============================================================================
# Backend Deployment Targets
# ==============================================================================

# Deploy the agent remotely
# Usage: make deploy [AGENT_IDENTITY=true] [SECRETS="KEY=SECRET_ID,..."] - Set AGENT_IDENTITY=true to enable per-agent IAM identity (Preview)
deploy:
	# Export dependencies to requirements file using uv export.
	(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > app/app_utils/.requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > app/app_utils/.requirements.txt) && \
	PROJECT_ID=$$(grep -E '^GOOGLE_CLOUD_PROJECT=' app/.env | cut -d '=' -f2) && \
	ARTIFACTS_BUCKET="$$PROJECT_ID-immersion-day-template-artifacts" && \
	rm -f app/.adk/session.db && \
	uv run -m app.app_utils.deploy \
		--source-packages=./app \
		--entrypoint-module=app.agent_engine_app \
		--entrypoint-object=agent_engine \
		--requirements-file=app/app_utils/.requirements.txt \
		--service-account="immersion-day-template-app@$$PROJECT_ID.iam.gserviceaccount.com" \
		--set-env-vars="ARTIFACTS_BUCKET_NAME=$$ARTIFACTS_BUCKET" \
		$(if $(AGENT_IDENTITY),--agent-identity) \
		$(if $(filter command line,$(origin SECRETS)),--set-secrets="$(SECRETS)")

# Alias for 'make deploy' for backward compatibility
backend: deploy

# Deploy the remote A2A agent to Cloud Run
build-a2a:
	@echo "==============================================================================="
	@echo "| 🐳 Building A2A Agent Container...                                          |"
	@echo "==============================================================================="
	@uv pip compile pyproject.toml -o requirements.txt
	gcloud builds submit --config app/a2a/cloudbuild.yaml .

deploy-a2a: build-a2a
	@echo "==============================================================================="
	@echo "| 🚀 Deploying A2A Agent to Cloud Run...                                      |"
	@echo "==============================================================================="
	@PROJECT_ID=$$(grep -E '^GOOGLE_CLOUD_PROJECT=' app/.env | cut -d '=' -f2) && \
	LOCATION=$$(grep -E '^GOOGLE_DEPLOYMENT_LOCATION=' app/.env | cut -d '=' -f2) && \
	NOAUTH_URL=$$(grep -E '^CLOUD_RUN_NOAUTH_MCP_URL=' app/.env | cut -d '=' -f2) && \
	DATASTORE=$$(grep -E '^VERTEX_AI_SEARCH_DATASTORE=' app/.env | cut -d '=' -f2) && \
	gcloud run deploy a2a-hello-world \
		--image gcr.io/$$PROJECT_ID/a2a-hello-world \
		--project $$PROJECT_ID \
		--region $$LOCATION \
		--platform managed \
		--no-allow-unauthenticated \
		--update-env-vars GOOGLE_CLOUD_PROJECT=$$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$$LOCATION,GOOGLE_GENAI_USE_VERTEXAI=1,CLOUD_RUN_NOAUTH_MCP_URL=$$NOAUTH_URL,VERTEX_AI_SEARCH_DATASTORE=$$DATASTORE

# ==============================================================================
# Infrastructure Setup
# ==============================================================================

# Set up development environment resources using Terraform
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)



# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit and integration tests
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# ==============================================================================
# Agent Evaluation
# ==============================================================================

# Run agent evaluation using ADK eval
# Usage: make eval [EVALSET=tests/eval/evalsets/basic.evalset.json] [EVAL_CONFIG=tests/eval/eval_config.json] [ARGS="--print_detailed_results"]
eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./app $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,)) \
		$(ARGS)

# Run evaluation with all evalsets
eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

# Run code quality checks (codespell, ruff, ty)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .

# ==============================================================================
# Gemini Enterprise Integration
# ==============================================================================

# Register the deployed agent to Gemini Enterprise
# Usage: make register-gemini-enterprise (interactive - will prompt for required details)
# For non-interactive use, set env vars: ID or GEMINI_ENTERPRISE_APP_ID (full GE resource name)
# Optional env vars: GEMINI_DISPLAY_NAME, GEMINI_DESCRIPTION, GEMINI_TOOL_DESCRIPTION, AGENT_ENGINE_ID
register-gemini-enterprise:
	@uvx agent-starter-pack@0.39.6 register-gemini-enterprise

# ==============================================================================
# Authentication Tokens
# ==============================================================================

# Print a short-lived OAuth 2.0 access token
print-access-token:
	@gcloud auth print-access-token

# Print an identity token (OIDC token)
print-id-token:
	@gcloud auth print-identity-token

# ==============================================================================
# Skills
# ==============================================================================

# Push local skills to GCS
push-skills:
	@echo "==============================================================================="
	@echo "| 🚀 Pushing local skills to GCS...                                           |"
	@echo "==============================================================================="
	@SKILLS_URI=$$(grep -E '^SKILLS_URI=' app/.env | cut -d '=' -f2) && \
	if [ -z "$$SKILLS_URI" ]; then \
		echo "Error: SKILLS_URI is not set in app/.env"; \
		exit 1; \
	fi; \
	/Users/julienrzeznik/google-cloud-sdk/bin/gcloud storage cp -r app/skills/* $$SKILLS_URI/

