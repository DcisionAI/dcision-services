#!/bin/bash
set -euo pipefail

# Configurable variables
PROJECT_ID="dcisionai"
SERVICE_NAME="gpt4all"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/gpt4all-backend"
MEMORY="12Gi"
CPU="4"
PORT="8000"
GCS_BUCKET="dcisionai-models"
MODEL_FILE="ggml-gpt4all-j-v1.3-groovy.bin"

# Build the Docker image

echo "Building Docker image..."
gcloud builds submit --tag $IMAGE

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port $PORT \
  --memory=$MEMORY \
  --cpu=$CPU \
  --set-env-vars=GCS_BUCKET=$GCS_BUCKET,GPT4ALL_MODEL_PATH=$MODEL_FILE

echo "Deployment complete!"
echo "Check service status with:"
echo "  gcloud run services describe $SERVICE_NAME --region $REGION" 