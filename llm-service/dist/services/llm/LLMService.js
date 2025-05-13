"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.LLMServiceImpl = void 0;
const openai_1 = __importDefault(require("openai"));
/**
 * Basic LLM service supporting OpenAI and GPT4All-compatible endpoints.
 */
class LLMServiceImpl {
    constructor(provider) {
        this.provider = provider;
        if (provider === 'gpt4all') {
            const url = process.env.GPT4ALL_API_URL;
            if (!url) {
                throw new Error('Missing GPT4ALL_API_URL environment variable');
            }
            // Use OpenAI-compatible client pointing to GPT4All server
            this.client = new openai_1.default({ apiKey: '', baseURL: url });
            this.model = process.env.GPT4ALL_MODEL || 'gpt4all';
        }
        else {
            const apiKey = process.env.OPENAI_API_KEY;
            if (!apiKey) {
                throw new Error('Missing OPENAI_API_KEY environment variable');
            }
            this.client = new openai_1.default({ apiKey });
            this.model = 'gpt-4-turbo-preview';
        }
    }
    /**
     * Interpret a user problem description and return parsed JSON or raw interpretation.
     */
    async interpretIntent(description) {
        var _a, _b, _c;
        const systemPrompt = 'You are an expert decision-modeling analyst. Interpret the business problem and return your analysis as JSON.';
        const messages = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: `Problem description: ${description}` },
        ];
        const response = await this.client.chat.completions.create({
            model: this.model,
            messages,
        });
        const content = ((_c = (_b = (_a = response.choices) === null || _a === void 0 ? void 0 : _a[0]) === null || _b === void 0 ? void 0 : _b.message) === null || _c === void 0 ? void 0 : _c.content) || '';
        try {
            return JSON.parse(content);
        }
        catch {
            return { interpretation: content };
        }
    }
}
exports.LLMServiceImpl = LLMServiceImpl;
