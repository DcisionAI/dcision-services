#!/usr/bin/env bash
set -euo pipefail
# Ensure we run from the repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"
cd "$ROOT_DIR"
echo "Working directory: $(pwd)"

#------------------------------------------------------------------------------
# Deploy both solver-service and mcp-service to GCP Cloud Run
# Requirements: gcloud SDK installed, authenticated, and project configured
# Usage: bash scripts/deploy-services.sh [PROJECT_ID] [REGION]
#------------------------------------------------------------------------------

# GCP project and region (override via args or rely on gcloud config)
PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-us-central1}

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: GCP project ID not provided and gcloud config is empty."
  echo "Usage: bash scripts/deploy-services.sh [PROJECT_ID] [REGION]"
  exit 1
fi

echo "Using GCP project: $PROJECT_ID"
echo "Deploy region:      $REGION"

### Build & push solver-service
echo "\n=== Building and pushing solver-service ==="
gcloud builds submit solver-service \
  --project="$PROJECT_ID" \
  --tag="gcr.io/$PROJECT_ID/solver-service:latest"

echo "Deploying solver-service to Cloud Run..."
gcloud run deploy solver-service \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="gcr.io/$PROJECT_ID/solver-service:latest" \
  --platform=managed \
  --allow-unauthenticated

# Capture the solver-service URL
SOLVER_URL=$(gcloud run services describe solver-service \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --platform=managed \
  --format="value(status.url)")
echo "Solver service URL: $SOLVER_URL"

### Build & push mcp-service
echo "\n=== Building and pushing mcp-service ==="
gcloud builds submit mcp-service \
  --project="$PROJECT_ID" \
  --tag="gcr.io/$PROJECT_ID/mcp-service:latest"

echo "Deploying mcp-service to Cloud Run..."
gcloud run deploy mcp-service \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="gcr.io/$PROJECT_ID/mcp-service:latest" \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="SOLVER_SERVICE_URL=$SOLVER_URL"

# Final service URLs
MCP_URL=$(gcloud run services describe mcp-service \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --platform=managed \
  --format="value(status.url)")

echo "\n--- Deployment complete ---"
echo "Solver service: $SOLVER_URL"
echo "MCP service:    $MCP_URL"