# How to Use LLM Service

## Test /chat with Postman or curl

You can test the LLM service with a simple chat request using the following example (adjust the endpoint if your service uses a different path).

### Example JSON Payload

```
{
  "prompt": "What is the capital of France?",
  "max_tokens": 32
}
```

### Curl Command

```
curl -X POST https://llm.dcisionai.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "max_tokens": 32
  }'
```

> **Note:** Replace `/chat` with the actual endpoint if it differs, and adjust the payload fields as needed for your LLM API. 