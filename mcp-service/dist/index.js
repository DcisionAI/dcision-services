"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const axios_1 = __importDefault(require("axios"));
const app = (0, express_1.default)();
app.use(body_parser_1.default.json());
// Environment variable for solver-service URL
const SOLVER_URL = process.env.SOLVER_SERVICE_URL || 'http://localhost:8080';
app.post('/mcp/submit', async (req, res) => {
    const mcp = req.body;
    const results = [];
    for (const step of mcp.protocol.steps) {
        try {
            if (step.action === 'collect_data') {
                // TODO: integrate airbyte-service
                results.push({ step, agent: 'DataIntegrationAgent', result: { message: 'Data collected (mock)' } });
            }
            else if (step.action === 'build_model') {
                // Model building placeholder
                results.push({ step, agent: 'ModelBuilderAgent', result: { message: 'Model built (mock)' } });
            }
            else if (step.action === 'solve_model') {
                // Call solver-service
                let solverRes;
                if (mcp.context.problemType === 'vehicle_routing') {
                    solverRes = await axios_1.default.post(`${SOLVER_URL}/solve/vehicle-assignment`, mcp.model);
                }
                else {
                    // For non-VRP problems, send the model payload directly to /solve
                    solverRes = await axios_1.default.post(`${SOLVER_URL}/solve`, mcp.model);
                }
                results.push({ step, agent: 'ModelRunnerAgent', result: solverRes.data });
            }
            else if (step.action === 'explain_solution') {
                // TODO: integrate LLM-based explanation
                results.push({ step, agent: 'SolutionExplainerAgent', result: { explanation: 'Solution explained (mock)' } });
            }
            else {
                results.push({ step, agent: 'Unknown', result: null, error: 'No agent for this action' });
            }
        }
        catch (err) {
            // Capture detailed error from solver-service if available
            let errorMsg = err.message;
            if (err.response && err.response.data) {
                // Use 'detail' field from HTTPException, or full response body
                if (err.response.data.detail) {
                    errorMsg = err.response.data.detail;
                }
                else {
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
