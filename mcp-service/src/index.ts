import express from 'express';
import bodyParser from 'body-parser';
import axios from 'axios';
import cors from 'cors';

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
app.use(cors({
  origin: [
    'https://platform.dcisionai.com',
    'http://localhost:3000'
  ],
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));

// Environment variable for solver-service URL
const SOLVER_URL = process.env.SOLVER_SERVICE_URL || 'http://localhost:8080';
// Dynamic solver flows mapping
const flowMap: Record<string,string> = {};
// Fetch flows once and cache
const flowsPromise = axios.get(`${SOLVER_URL}/flows`)
  .then(resp => {
    resp.data.flows.forEach((f: any) => {
      flowMap[f.id] = f.endpoint;
    });
    console.log('Loaded solver flows:', Object.keys(flowMap));
  })
  .catch((err: any) => {
    console.error('Could not load solver flows:', err.message || err);
  });

app.post('/mcp/submit', async (req, res) => {
  const mcp: MCP = req.body;
  const results: OrchestrationResult[] = [];

  // Log the incoming payload for debugging
  console.log('MCP received:', JSON.stringify(mcp, null, 2));

  for (const step of mcp.protocol.steps) {
    try {
      if (step.action === 'collect_data') {
        // TODO: integrate airbyte-service
        results.push({ step, agent: 'DataIntegrationAgent', result: { message: 'Data collected (mock)' } });
      } else if (step.action === 'build_model') {
        // Model building placeholder
        results.push({ step, agent: 'ModelBuilderAgent', result: { message: 'Model built (mock)' } });
      } else if (step.action === 'solve_model') {
        // Call solver-service using dynamic flows
        await flowsPromise;
        const problemType = mcp.context?.problemType || mcp.model?.problemType || '';
        const endpoint = flowMap[problemType] || '/solve';
        const solverRes = await axios.post(`${SOLVER_URL}${endpoint}`, mcp.model);
        results.push({ step, agent: 'ModelRunnerAgent', result: solverRes.data });
      } else if (step.action === 'explain_solution') {
        // TODO: integrate LLM-based explanation
        results.push({ step, agent: 'SolutionExplainerAgent', result: { explanation: 'Solution explained (mock)' } });
      } else {
        results.push({ step, agent: 'Unknown', result: null, error: 'No agent for this action' });
      }
    } catch (err) {
      // Capture detailed error from solver-service if available
      const e: any = err;
      let errorMsg = e.message;
      if (e.response && e.response.data) {
        // Use 'detail' field from HTTPException, or full response body
        if (e.response.data.detail) {
          errorMsg = e.response.data.detail;
        } else {
          errorMsg = JSON.stringify(e.response.data);
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
// Alternative health endpoint for K8s
app.get('/healthz', (_req, res) => {
  res.json({ status: 'healthy' });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`MCP service listening on port ${port}`);
});