# How to Use Solver Service

## Test /solve with Postman or curl

You can test the solver-service with a simple linear programming (LP) model using the following example.

### Example JSON Payload

curl -X POST https://solver-service-219323644585.us-central1.run.app/solve \
       -H "Content-Type: application/json" \
       -d
'{
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
  },
  "name": "Simple Example",
  "description": "Maximize 2x + 3y subject to constraints"
}'
```

### Curl Command

```
curl -X POST https://solve.dcisionai.com/solve \
  -H "Content-Type: application/json" \
  -d '{
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
    },
    "name": "Simple Example",
    "description": "Maximize 2x + 3y subject to constraints"
  }'
``` 