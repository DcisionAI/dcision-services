#!/bin/bash

# Exit on error
set -e

# Variables (edit as needed)
PROJECT_ID="dcisionai"
SERVICE_NAME="solver-service"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# Build Docker image for linux/amd64 and push to GCR
echo "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -t $IMAGE . --push

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated

echo "Deployment complete!"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'

echo "Done." 