"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LLMServiceFactory = void 0;
const LLMService_1 = require("./LLMService");
/**
 * Factory to provide a singleton LLM service instance.
 */
class LLMServiceFactory {
    static getInstance() {
        if (!this.instance) {
            const provider = process.env.LLM_PROVIDER || 'openai';
            this.instance = new LLMService_1.LLMServiceImpl(provider);
        }
        return this.instance;
    }
}
exports.LLMServiceFactory = LLMServiceFactory;
