#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t solver-service .

# Run the container locally for testing
echo "Running container locally..."
docker run -p 8000:8000 --name solver-service solver-service

# To deploy to Google Cloud Run:
# 1. Make sure you have gcloud CLI installed and configured
# 2. Run: gcloud builds submit --config cloudbuild.yaml
# 3. The service will be available at: https://solver-service-<hash>-uc.a.run.app

# To deploy to AWS ECS:
# 1. Make sure you have AWS CLI configured
# 2. Create an ECS cluster and task definition
# 3. Push the image to ECR: aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
# 4. Tag and push: docker tag solver-service:latest <account-id>.dkr.ecr.<region>.amazonaws.com/solver-service:latest
# 5. docker push <account-id>.dkr.ecr.<region>.amazonaws.com/solver-service:latest
# 6. Update the ECS service with the new image

# To deploy to Azure:
# 1. Make sure you have Azure CLI configured
# 2. Create a Container Registry: az acr create --resource-group <group> --name <registry> --sku Basic
# 3. Build and push: az acr build --registry <registry> --image solver-service:latest .
# 4. Create Container Instance: az container create --resource-group <group> --name solver-service --image <registry>.azurecr.io/solver-service:latest --dns-name-label solver-service --ports 8000 