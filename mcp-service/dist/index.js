"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const axios_1 = __importDefault(require("axios"));
const cors_1 = __importDefault(require("cors"));
const app = (0, express_1.default)();
app.use(body_parser_1.default.json());
app.use((0, cors_1.default)({
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
// Dynamic flows mapping (populated at startup)
let flowMap = {};
// Load available solver flows
(async function loadFlows() {
    try {
        const resp = await axios_1.default.get(`${SOLVER_URL}/flows`);
        resp.data.flows.forEach((f) => {
            flowMap[f.id] = f.endpoint;
        });
        console.log('Loaded solver flows:', Object.keys(flowMap));
    }
    catch (err) {
        const e = err;
        console.error('Could not load solver flows:', e.message || e);
    }
})();
app.post('/mcp/submit', async (req, res) => {
    var _a, _b;
    const mcp = req.body;
    const results = [];
    // Log the incoming payload for debugging
    console.log('MCP received:', JSON.stringify(mcp, null, 2));
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
                // Call solver-service using dynamic flows
                const problemType = ((_a = mcp.context) === null || _a === void 0 ? void 0 : _a.problemType) || ((_b = mcp.model) === null || _b === void 0 ? void 0 : _b.problemType) || '';
                const endpoint = flowMap[problemType] || '/solve';
                const solverRes = await axios_1.default.post(`${SOLVER_URL}${endpoint}`, mcp.model);
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
            const e = err;
            let errorMsg = e.message;
            if (e.response && e.response.data) {
                // Use 'detail' field from HTTPException, or full response body
                if (e.response.data.detail) {
                    errorMsg = e.response.data.detail;
                }
                else {
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
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`MCP service listening on port ${port}`);
});
