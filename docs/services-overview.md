# DcisionAI Services Overview

This document provides a comprehensive overview of the core microservices powering DcisionAI's decision intelligence platform: **llm.dcisionai.com**, **mcp.dcisionai.com**, and **solve.dcisionai.com**. It covers what each service does, their architecture, how to make changes, deploy, and how they work together.

---

## 1. Service Overview

### llm.dcisionai.com

- **Purpose:** Provides a local, OpenAI-compatible LLM API for natural language understanding and generation, used for intent interpretation, solution explanation, and more.
- **Tech:** Python, FastAPI, GPT4All, Google Cloud Storage for model files.
- **Endpoints:**
  - `/v1/chat/completions`: OpenAI-style chat completions.
  - `/health`: Readiness check.
- **Deployment:** Containerized, deployable to Cloud Run. Model file is downloaded from GCS at startup.

### mcp.dcisionai.com

- **Purpose:** Orchestrates the end-to-end decision process. Receives a structured "MCP" (Model-Context-Protocol) request, coordinates data collection, model building, solving, and explanation.
- **Tech:** Node.js, Express.
- **Endpoints:**
  - `/mcp/submit`: Accepts an MCP JSON, executes protocol steps (collect, build, solve, explain).
  - `/health`: Health check.
- **Deployment:** Containerized, deployable to Cloud Run. Communicates with solve.dcisionai.com and (optionally) llm.dcisionai.com.

### solve.dcisionai.com

- **Purpose:** Solves optimization problems (LP, MIP, VRP, scheduling, etc.) for various domains (FleetOps, Workforce).
- **Tech:** Python, FastAPI, OR-Tools, Pydantic.
- **Endpoints:**
  - `/solve`: Accepts a model, returns solution.
  - `/health`: Health check.
- **Domains Supported:** 
  - `fleetops` (vehicle assignment, fleet mix, maintenance, fuel)
  - `workforce` (scheduling, skill matching, shift optimization, workload balancing)
- **Deployment:** Containerized, deployable to Cloud Run.

---

## 2. Architecture

- **High-Level Flow:**
  1. User submits a business problem (via UI or API).
  2. **llm.dcisionai.com** interprets the intent and returns a structured MCP.
  3. **mcp.dcisionai.com** orchestrates the protocol: collects data, builds the model, calls **solve.dcisionai.com**, and (optionally) requests explanations from the LLM backend.
  4. **solve.dcisionai.com** solves the optimization problem and returns results to **mcp.dcisionai.com**, which aggregates and returns the final response.

- **Data Flow:**
  - llm.dcisionai.com ↔ mcp.dcisionai.com ↔ solve.dcisionai.com
  - All services expose REST APIs and communicate via HTTP.

---

## 3. How-To Guides

### Making Changes

- **llm.dcisionai.com:**
  - Edit `main.py` for API logic.
  - Update model or requirements as needed.
  - Test locally with `uvicorn main:app --reload`.
- **mcp.dcisionai.com:**
  - Edit `src/index.ts` for orchestration logic.
  - Add new protocol steps or integrate new agents.
  - Test with `npm run dev`.
- **solve.dcisionai.com:**
  - Add/modify solvers in `src/core/solver.py`.
  - Add new domains in `src/domains/`.
  - Test with `pytest` or the provided test scripts.

### Local Development & Testing

- Each service can be run locally (see respective Dockerfiles and scripts).
- Use sample payloads in `mcp-service/sample-mcp-*.json` for testing.
- Health checks available at `/health` for all services.

### Deployment

- See `docs/deployment.md` for detailed Cloud Run deployment steps.
- Each service has a deploy script (`deploy-llm.sh`, `deploy_mcp_service.sh`, `deploy.sh`).
- Set required environment variables (API keys, model paths, service URLs).

---

## 4. How They Work

### Example Flow

1. **Intent Interpretation:**  
   User describes a business problem. **llm.dcisionai.com** interprets and returns a structured MCP.
2. **MCP Orchestration:**  
   **mcp.dcisionai.com** executes protocol steps:  
   - `collect_data` (future: integrate with data connectors)  
   - `build_model` (future: model builder agent)  
   - `solve_model` (calls **solve.dcisionai.com**)  
   - `explain_solution` (future: LLM-based explanation)
3. **Solving:**  
   **solve.dcisionai.com** receives a model, selects the appropriate solver (LP, MIP, VRP, etc.), and returns the solution.

### Extending the Platform

- **Add a new domain:**  
  Implement a new intent agent in `solver-service/src/domains/`, register in the factory.
- **Add a new solver:**  
  Implement in `solver-service/src/core/solver.py`, add to the `solvers` dict.
- **Add a new protocol step:**  
  Update **mcp.dcisionai.com**'s orchestration logic in `src/index.ts`.

---

## 5. References

- [Deployment Guide](./deployment.md)
- [Sample MCP Payloads](../mcp-service/sample-mcp-*.json)
- [gpt4all-backend/deploy-llm.sh](../gpt4all-backend/deploy-llm.sh)
- [solver-service/deploy.sh](../solver-service/deploy.sh)

---
_Last updated: 2025-05-13_ 