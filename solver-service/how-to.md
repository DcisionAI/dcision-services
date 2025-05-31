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

## Example: Labor Scheduling

```bash
curl -X POST https://<your-solver-service>/solve/labor-scheduling \
  -H "Content-Type: application/json" \
  -d '{
    "employees": [
      {"id": 1, "name": "Alice", "skills": ["driver"], "max_hours": 40, "hourly_rate": 20, "availability": []},
      {"id": 2, "name": "Bob", "skills": ["loader"], "max_hours": 40, "hourly_rate": 18, "availability": []}
    ],
    "shifts": [
      {"id": 1, "name": "Morning"},
      {"id": 2, "name": "Evening"}
    ],
    "time_horizon": 7,
    "constraints": {
      "min_rest_hours": 8,
      "max_consecutive_hours": 8,
      "coverage_requirements": {"1": 1, "2": 1},
      "skill_requirements": {"1": ["driver"], "2": ["loader"]}
    },
    "objective": "minimize_cost"
  }'
```

## Example: Equipment Allocation

```bash
curl -X POST https://<your-solver-service>/solve/equipment-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "equipment": [
      {"id": 0, "type": "crane", "capacity": 10, "cost": 100},
      {"id": 1, "type": "forklift", "capacity": 5, "cost": 60}
    ],
    "tasks": [
      {"id": 0, "location": {"id": 0, "latitude": 0, "longitude": 0, "name": "SiteA"}, "duration": 2, "required_skills": [], "priority": 1, "time_window": [0, 8]},
      {"id": 1, "location": {"id": 1, "latitude": 0, "longitude": 0, "name": "SiteB"}, "duration": 3, "required_skills": [], "priority": 1, "time_window": [0, 8]}
    ],
    "locations": [
      {"id": 0, "latitude": 0, "longitude": 0, "name": "SiteA"},
      {"id": 1, "latitude": 0, "longitude": 0, "name": "SiteB"}
    ],
    "cost_matrix": [[10, 20], [15, 12]],
    "constraints": {
      "max_equipment_per_location": 1,
      "min_tasks_per_equipment": 1,
      "assignment_restrictions": []
    },
    "objective": "minimize_total_cost"
  }'
```

## Example: Material Delivery Planning

```bash
curl -X POST https://<your-solver-service>/solve/material-delivery-planning \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {"id": 0, "capacity": 10},
      {"id": 1, "capacity": 10}
    ],
    "deliveries": [
      {"id": 1, "location": {"id": 1, "latitude": 0, "longitude": 0, "name": "Customer1"}, "duration": 2, "required_skills": [], "priority": 1, "time_window": [2, 6]},
      {"id": 2, "location": {"id": 2, "latitude": 0, "longitude": 0, "name": "Customer2"}, "duration": 3, "required_skills": [], "priority": 1, "time_window": [4, 8]}
    ],
    "locations": [
      {"id": 0, "latitude": 0, "longitude": 0, "name": "Depot"},
      {"id": 1, "latitude": 0, "longitude": 0, "name": "Customer1"},
      {"id": 2, "latitude": 0, "longitude": 0, "name": "Customer2"}
    ],
    "time_windows": [[0, 10], [2, 6], [4, 8]],
    "distance_matrix": [[0, 5, 7], [5, 0, 3], [7, 3, 0]],
    "constraints": {
      "vehicle_capacity": 10,
      "max_route_time": 10,
      "delivery_time_windows": [[2, 6], [4, 8]]
    },
    "objective": "minimize_total_distance"
  }'
```

## Example: Risk Simulation

```bash
curl -X POST https://<your-solver-service>/solve/risk-simulation \
  -H "Content-Type: application/json" \
  -d '{
    "project_network": [
      {"id": 1, "name": "Start", "predecessors": []},
      {"id": 2, "name": "TaskA", "predecessors": [1]},
      {"id": 3, "name": "TaskB", "predecessors": [2]}
    ],
    "risk_factors": [
      {"task_id": 1, "mean": 2, "stddev": 0.2},
      {"task_id": 2, "mean": 3, "stddev": 0.5},
      {"task_id": 3, "mean": 4, "stddev": 0.3}
    ],
    "num_simulations": 1000,
    "objective": "estimate_risk"
  }'
``` 