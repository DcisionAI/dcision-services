# DcisionAI Services

This repository contains the backend services for **DcisionAI**, including:

- **solver-service**: Optimization solver implemented in Python (FastAPI).
- **mcp-service**: MCP orchestration and API gateway (Node.js/Express).
- **llm-service**: LLM-powered intent interpretation and chat (Node.js/Express).
- **gpt4all-backend**: OpenAI-compatible LLM backend using GPT4All (Python/FastAPI).

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

## Local Development

### Prerequisites
- Node.js (v18 or later) and Yarn
- Python 3.x and pip

### Running Locally

#### Solver Service (Python FastAPI + OR-Tools)
```bash
cd solver-service
pip install -r requirements.txt
pip install -e .
uvicorn src.api.routes:app --reload
```

#### MCP Service (Node.js/Express)
```bash
cd mcp-service
npm install
npm run dev
```

#### LLM Service (Node.js/Express)
```bash
cd llm-service
yarn install
yarn dev
```

#### GPT4All Backend (Python/FastAPI)
```bash
cd gpt4all-backend
pip install -r requirements.txt
python main.py
```

## Cloud Run Deployment

Each service can be built and deployed to Cloud Run. See `docs/deployment.md` and service-specific deploy scripts for details.

---
_Last updated: 2025-05-13_