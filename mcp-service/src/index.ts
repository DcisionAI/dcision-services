import express from 'express';
import bodyParser from 'body-parser';
import axios from 'axios';

// Basic MCP interfaces
interface MCP {
  sessionId: string;
  version: string;
  created: string;
  lastModified: string;
  status: string;
  model: any;
  context: { problemType: string };
  protocol: { steps: { action: string; required: boolean }[] };
}

interface OrchestrationResult {
  step: { action: string; required: boolean };
  agent: string;
  result: any;
  error?: string;
}

const app = express();
app.use(bodyParser.json());

// Environment variable for solver-service URL
const SOLVER_URL = process.env.SOLVER_SERVICE_URL || 'http://localhost:8080';

app.post('/mcp/submit', async (req, res) => {
  const mcp: MCP = req.body;
  const results: OrchestrationResult[] = [];

  for (const step of mcp.protocol.steps) {
    try {
      if (step.action === 'collect_data') {
        // TODO: integrate airbyte-service
        results.push({ step, agent: 'DataIntegrationAgent', result: { message: 'Data collected (mock)' } });
      } else if (step.action === 'build_model') {
        // Model building placeholder
        results.push({ step, agent: 'ModelBuilderAgent', result: { message: 'Model built (mock)' } });
      } else if (step.action === 'solve_model') {
        // Call solver-service
        let solverRes;
        if (mcp.context.problemType === 'vehicle_routing') {
          solverRes = await axios.post(`${SOLVER_URL}/solve/vehicle-assignment`, mcp.model);
        } else {
          // For non-VRP problems, send the model payload directly to /solve
          solverRes = await axios.post(`${SOLVER_URL}/solve`, mcp.model);
        }
        results.push({ step, agent: 'ModelRunnerAgent', result: solverRes.data });
      } else if (step.action === 'explain_solution') {
        // TODO: integrate LLM-based explanation
        results.push({ step, agent: 'SolutionExplainerAgent', result: { explanation: 'Solution explained (mock)' } });
      } else {
        results.push({ step, agent: 'Unknown', result: null, error: 'No agent for this action' });
      }
    } catch (err: any) {
      // Capture detailed error from solver-service if available
      let errorMsg = err.message;
      if (err.response && err.response.data) {
        // Use 'detail' field from HTTPException, or full response body
        if (err.response.data.detail) {
          errorMsg = err.response.data.detail;
        } else {
          errorMsg = JSON.stringify(err.response.data);
        }
      }
      results.push({ step, agent: 'ModelRunnerAgent', result: null, error: errorMsg });
    }
  }

  res.json({ sessionId: mcp.sessionId, status: 'completed', results });
});

app.get('/health', (_req, res) => {
  res.json({ status: 'healthy' });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`MCP service listening on port ${port}`);
});