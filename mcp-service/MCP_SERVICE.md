# MCP Service Deep Dive

## Overview
The MCP (Machine Configurable Problem) Service is an orchestration layer for optimization workflows. It receives high-level problem definitions (MCP configs), manages protocol steps (such as data collection, model building, solving, and explanation), and delegates the actual solving to the solver-service. It is designed for flexibility and extensibility across domains like FleetOps and Workforce Scheduling.

---

## Endpoints

### 1. `/mcp/submit`
- **Method:** POST
- **Purpose:** Accepts an MCP config (JSON) describing the optimization problem, context, and protocol steps.
- **Input Schema:**
  - `sessionId`, `version`, `created`, `lastModified`, `status`: Metadata
  - `model`: The optimization model (can be generic LP/MIP or domain-specific)
  - `context`: Problem type, industry, environment, dataset
  - `protocol`: Steps to execute (e.g., solve_model, explain_solution)
- **How it works:**
  1. Receives the MCP config and parses the protocol steps.
  2. For each step:
     - If `solve_model`, forwards the model to the solver-service (choosing the right endpoint based on problem type).
     - Handles other steps (e.g., data collection, explanation) as needed.
  3. Aggregates results and errors for each step.
  4. Returns a summary response with results for all steps.

### 2. `/health`
- **Method:** GET
- **Purpose:** Health check endpoint.

---

## Request/Response Flow
1. **Request Received:**
   - The service receives a POST to `/mcp/submit` with an MCP config.
2. **Input Validation:**
   - Validates the MCP config structure and protocol steps.
3. **Step Orchestration:**
   - Iterates through protocol steps (e.g., solve_model, explain_solution).
   - For `solve_model`, determines the problem type and calls the appropriate solver-service endpoint.
4. **Solver Interaction:**
   - For vehicle routing, calls `/solve/vehicle-assignment` on the solver-service.
   - For LP/MIP, calls `/solve` on the solver-service.
5. **Result Aggregation:**
   - Collects results and errors for each step.
6. **Response:**
   - Returns a JSON response with sessionId, status, and results for each protocol step.

---

## Deep Dive: Orchestration Logic
- **Protocol Steps:**
  - Each step in the protocol is handled in sequence.
  - Steps can include data collection, model building, solving, and explanation.
- **Model Submission:**
  - The model can be a generic LP/MIP or a domain-specific structure (e.g., vehicle assignment).
  - The MCP service determines the correct solver endpoint based on the problem type in the context.
- **Error Handling:**
  - Captures and returns detailed errors from the solver-service or internal logic.

---

## Extensibility
- New protocol steps can be added (e.g., data integration, human-in-the-loop, explainability).
- Supports multiple domains by routing to the appropriate solver endpoint.

---

## Example Usage
- See `how-to.md` for sample MCP payloads and curl commands. 