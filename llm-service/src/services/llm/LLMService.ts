import OpenAI from 'openai';

export type LLMProvider = 'openai' | 'gpt4all';

/**
 * Basic LLM service supporting OpenAI and GPT4All-compatible endpoints.
 */
export class LLMServiceImpl {
  private client: any;
  private model: string;

  constructor(private provider: LLMProvider) {
    if (provider === 'gpt4all') {
      const url = process.env.GPT4ALL_API_URL;
      if (!url) {
        throw new Error('Missing GPT4ALL_API_URL environment variable');
      }
      // Use OpenAI-compatible client pointing to GPT4All server
      this.client = new OpenAI({ apiKey: '', baseURL: url });
      this.model = process.env.GPT4ALL_MODEL || 'gpt4all';
    } else {
      const apiKey = process.env.OPENAI_API_KEY;
      if (!apiKey) {
        throw new Error('Missing OPENAI_API_KEY environment variable');
      }
      this.client = new OpenAI({ apiKey });
      this.model = 'gpt-4-turbo-preview';
    }
  }

  /**
   * Interpret a user problem description and return parsed JSON or raw interpretation.
   */
  async interpretIntent(description: string): Promise<any> {
    const systemPrompt =
      'You are an expert decision-modeling analyst. Interpret the business problem and return your analysis as JSON.';
    const messages = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Problem description: ${description}` },
    ];
    const response = await this.client.chat.completions.create({
      model: this.model,
      messages,
    });
    const content = response.choices?.[0]?.message?.content || '';
    try {
      return JSON.parse(content);
    } catch {
      return { interpretation: content };
    }
  }
}