# Core Services Deployment Guide

This guide walks through deploying the **solver-service**, **mcp-service**, **llm-service**, and **gpt4all-backend** microservices to Google Cloud Run, and configuring custom domains.

## Prerequisites
- Google Cloud SDK installed and authenticated (`gcloud auth login`).
- `gcloud` configured to the target project:
  ```bash
  gcloud config set project YOUR_PROJECT_ID
  ```
- User or service account with roles:
  - Cloud Build Editor (`roles/cloudbuild.builds.editor`)
  - Cloud Run Admin (`roles/run.admin`)
  - Service Account User (`roles/iam.serviceAccountUser`)

## Cloud Run Custom Domain Mappings

| Service         | Cloud Run Service Name | Custom Domain                | Example Endpoint                  |
|----------------|-----------------------|------------------------------|-----------------------------------|
| LLM Backend    | gpt4all               | llm.dcisionai.com            | https://llm.dcisionai.com/health  |
| MCP Service    | mcp-service           | mcp.dcisionai.com            | https://mcp.dcisionai.com/health  |
| Solver Service | solver-service        | solve.dcisionai.com          | https://solve.dcisionai.com/health|

All custom domains are mapped via Cloud Run domain mappings and require a CNAME record in your DNS provider (e.g., GoDaddy):

- **Name:** (e.g., `llm`, `mcp`, `solve`)
- **Type:** CNAME
- **Value:** ghs.googlehosted.com.

## Testing Deployed Endpoints

**Health Check:**
```sh
curl https://llm.dcisionai.com/health
curl https://mcp.dcisionai.com/health
curl https://solve.dcisionai.com/health
```

**LLM Chat Completion Example:**
```sh
curl -X POST "https://llm.dcisionai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

## 1. Deploy `solver-service`

1. From the repository root, submit the Python solver-service to Cloud Build:
   ```bash
   gcloud builds submit solver-service \
     --project=$PROJECT_ID \
     --tag=gcr.io/$PROJECT_ID/solver-service:latest
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy solver-service \
     --image=gcr.io/$PROJECT_ID/solver-service:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated
   ```

3. Capture its URL:
   ```bash
   SOLVER_URL=$(gcloud run services describe solver-service \
     --region=us-central1 --format="value(status.url)")
   echo "Solver service endpoint: $SOLVER_URL"
   ```

## 2. Deploy `mcp-service`

1. Build and push the Node/Express MCP server:
   ```bash
   gcloud builds submit mcp-service \
     --project=$PROJECT_ID \
     --tag=gcr.io/$PROJECT_ID/mcp-service:latest
   ```

2. Deploy to Cloud Run, wiring in the solver URL:
   ```bash
   gcloud run deploy mcp-service \
     --image=gcr.io/$PROJECT_ID/mcp-service:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --set-env-vars SOLVER_SERVICE_URL="$SOLVER_URL"
   ```

> **Note:** Cloud Run automatically provides a `PORT` environment variable (default 8080).

3. Verify both services are running:
   ```bash
   gcloud run services list --region=us-central1
   ```

## 3. Deploy `llm-service` and `gpt4all-backend`

- See the main README and `gpt4all-backend/deploy-llm.sh` for recommended build and deploy scripts for the LLM backend.
- For `llm-service`, use a similar `gcloud builds submit` and `gcloud run deploy` process as above.

## 4. Automated Deployment Script

You can also deploy both services together:
```bash
bash scripts/deploy-services.sh YOUR_PROJECT_ID us-central1
```

This script will:
1. Build & push `solver-service`
2. Deploy `solver-service` and capture its URL
3. Build & push `mcp-service`
4. Deploy `mcp-service` with the correct env var

---
_Last updated: 2025-05-13_