"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const body_parser_1 = __importDefault(require("body-parser"));
const LLMServiceFactory_1 = require("./services/llm/LLMServiceFactory");
async function main() {
    const app = (0, express_1.default)();
    app.use((0, cors_1.default)());
    app.use(body_parser_1.default.json());
    // Initialize LLM service
    const llmService = LLMServiceFactory_1.LLMServiceFactory.getInstance();
    // Health check
    app.get('/health', (_req, res) => {
        res.json({ status: 'healthy', provider: process.env.LLM_PROVIDER });
    });
    // Interpret intent
    app.post('/interpret-intent', async (req, res) => {
        try {
            const { description } = req.body;
            if (!description) {
                return res.status(400).json({ error: 'Missing description in request body' });
            }
            const result = await llmService.interpretIntent(description);
            res.json(result);
        }
        catch (err) {
            console.error('Error /interpret-intent:', err);
            res.status(500).json({ error: err.message });
        }
    });
    // (Additional endpoints can be added here)
    const port = parseInt(process.env.PORT || '3000', 10);
    app.listen(port, () => {
        console.log(`LLM service listening on port ${port}`);
    });
}
main().catch(err => {
    console.error('Failed to start LLM service:', err);
    process.exit(1);
});
