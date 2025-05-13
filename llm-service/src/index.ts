import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { LLMServiceFactory } from './services/llm/LLMServiceFactory';

async function main() {
  const app = express();
  app.use(cors());
  app.use(bodyParser.json());

  // Initialize LLM service
  const llmService = LLMServiceFactory.getInstance();

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
    } catch (err: any) {
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