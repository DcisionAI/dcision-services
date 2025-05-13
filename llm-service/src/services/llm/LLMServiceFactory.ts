import { LLMServiceImpl, LLMProvider } from './LLMService';

/**
 * Factory to provide a singleton LLM service instance.
 */
export class LLMServiceFactory {
  private static instance: LLMServiceImpl;

  static getInstance(): LLMServiceImpl {
    if (!this.instance) {
      const provider = (process.env.LLM_PROVIDER as LLMProvider) || 'gpt4all';
      this.instance = new LLMServiceImpl(provider);
    }
    return this.instance;
  }
}