# How to Use MCP Service

## Test /mcp/submit with Postman or curl

You can test the MCP service with a simple linear programming (LP) model using the following example.

### Example JSON Payload

```
{
  "sessionId": "simple-lp-session-001",
  "version": "1.0",
  "created": "2025-05-10T12:00:00Z",
  "lastModified": "2025-05-10T12:00:00Z",
  "status": "pending",
  "model": {
    "variables": [
      { "name": "x", "type": "continuous", "lower_bound": 0, "upper_bound": 10 },
      { "name": "y", "type": "continuous", "lower_bound": 0, "upper_bound": 10 }
    ],
    "constraints": [
      { "expression": "x + y", "operator": "<=", "rhs": 10 },
      { "expression": "x + -1*y", "operator": ">=", "rhs": 3 }
    ],
    "objective": {
      "expression": "2*x + 3*y",
      "type": "maximize"
    }
  },
  "context": {
    "problemType": "linear_programming",
    "industry": "test",
    "environment": { "region": "local", "timezone": "UTC" },
    "dataset": { "internalSources": [] }
  },
  "protocol": {
    "steps": [
      { "action": "solve_model", "required": true }
    ],
    "allowPartialSolutions": false,
    "explainabilityEnabled": false,
    "humanInTheLoop": { "required": false }
  }
}
```

### Curl Command

```
curl -X POST https://mcp.dcisionai.com/mcp/submit \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "simple-lp-session-001",
    "version": "1.0",
    "created": "2025-05-10T12:00:00Z",
    "lastModified": "2025-05-10T12:00:00Z",
    "status": "pending",
    "model": {
      "variables": [
        { "name": "x", "type": "continuous", "lower_bound": 0, "upper_bound": 10 },
        { "name": "y", "type": "continuous", "lower_bound": 0, "upper_bound": 10 }
      ],
      "constraints": [
        { "expression": "x + y", "operator": "<=", "rhs": 10 },
        { "expression": "x + -1*y", "operator": ">=", "rhs": 3 }
      ],
      "objective": {
        "expression": "2*x + 3*y",
        "type": "maximize"
      }
    },
    "context": {
      "problemType": "linear_programming",
      "industry": "test",
      "environment": { "region": "local", "timezone": "UTC" },
      "dataset": { "internalSources": [] }
    },
    "protocol": {
      "steps": [
        { "action": "solve_model", "required": true }
      ],
      "allowPartialSolutions": false,
      "explainabilityEnabled": false,
      "humanInTheLoop": { "required": false }
    }
  }'
``` 