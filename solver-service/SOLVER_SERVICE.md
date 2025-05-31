# Solver Service Deep Dive

> **Sample payloads and curl commands for all endpoints are available in [how-to.md](how-to.md).**

## Overview
The Solver Service is a backend microservice designed to solve a wide range of optimization problems, including linear programming (LP), mixed-integer programming (MIP), and domain-specific problems like vehicle routing, workforce scheduling, labor scheduling, equipment allocation, material delivery planning, and risk simulation. It exposes both generic and specialized endpoints, allowing for flexibility and domain power.

---

## Endpoints

### 1. Generic Endpoint: `/solve`
- **Method:** POST
- **Purpose:** Accepts any LP/MIP problem expressed as variables, constraints, and an objective.
- **Input Schema:**
  - `variables`: List of variables (name, type, bounds)
  - `constraints`: List of constraints (expression, operator, rhs)
  - `objective`: Objective function (expression, type)
  - `name`, `description`: Optional metadata
- **How it works:**
  1. Parses the input and creates variables in the solver (continuous, integer, or binary).
  2. Parses constraints and adds them to the solver.
  3. Sets the objective (minimize or maximize).
  4. Solves the problem using OR-Tools (GLOP for LP, SCIP for MIP).
  5. Returns the solution, including variable values and objective value.

### 2. Specialized Endpoint: `/solve/vehicle-assignment`
- **Method:** POST
- **Purpose:** Solves vehicle routing/assignment problems using a domain-specific schema.
- **Input Schema:**
  - `vehicles`: List of vehicles (id, type, capacity, operating_cost, maintenance_interval, fuel_efficiency)
  - `tasks`: List of tasks (id, location, duration, required_skills, priority, time_window, demand)
  - `locations`: List of locations (id, name, latitude, longitude)
  - `distance_matrix`: 2D array matching the order of locations
  - `constraints`: Dict of problem constraints
- **How it works:**
  1. Parses the input into domain objects.
  2. Creates assignment and sequencing variables for vehicles and tasks.
  3. Adds constraints for assignment, capacity, sequencing, and time windows.
  4. Sets the objective to minimize total distance.
  5. Solves the problem and returns assignments, sequences, and total distance.

### 3. Labor Scheduling: `/solve/labor-scheduling`
- **Method:** POST
- **Purpose:** Solves labor scheduling using CP-SAT (OR-Tools).
- **Input Schema:**
  - `employees`: List of employees (id, name, skills, max_hours, hourly_rate, availability)
  - `shifts`: List of shifts (id, name, start, end, etc.)
  - `time_horizon`: Number of days or periods
  - `constraints`: Dict (min_rest_hours, max_consecutive_hours, required_breaks, skill_requirements, coverage_requirements)
  - `objective`: "minimize_cost" or "maximize_coverage"
- **How it works:**
  1. Assigns employees to shifts over the time horizon.
  2. Enforces coverage, rest, and skill constraints.
  3. Optimizes for cost or coverage.
- **Sample MCP Payload:**
```json
{
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
}
```

### 4. Equipment Allocation: `/solve/equipment-allocation`
- **Method:** POST
- **Purpose:** Solves equipment allocation as a transportation/assignment problem (MIP).
- **Input Schema:**
  - `equipment`: List of equipment (id, type, capacity, cost)
  - `tasks`: List of tasks (id, location, duration, required_skills, priority, time_window)
  - `locations`: List of locations
  - `cost_matrix`: 2D array (equipment x task)
  - `constraints`: Dict (max_equipment_per_location, min_tasks_per_equipment, assignment_restrictions)
  - `objective`: "minimize_total_cost"
- **How it works:**
  1. Assigns equipment to tasks, respecting location and task constraints.
  2. Minimizes total cost.
- **Sample MCP Payload:**
```json
{
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
}
```

### 5. Material Delivery Planning: `/solve/material-delivery-planning`
- **Method:** POST
- **Purpose:** Solves material delivery planning as a VRPTW (Vehicle Routing Problem with Time Windows).
- **Input Schema:**
  - `vehicles`: List of vehicles (id, capacity, etc.)
  - `deliveries`: List of delivery tasks (id, location, duration, time_window)
  - `locations`: List of locations
  - `time_windows`: List of [start, end] for each location
  - `distance_matrix`: 2D array
  - `constraints`: Dict (vehicle_capacity, max_route_time, delivery_time_windows)
  - `objective`: "minimize_total_distance"
- **How it works:**
  1. Assigns deliveries to vehicles/routes, respecting capacity and time windows.
  2. Minimizes total distance.
- **Sample MCP Payload:**
```json
{
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
}
```

### 6. Risk Simulation: `/solve/risk-simulation`
- **Method:** POST
- **Purpose:** Runs Monte Carlo simulation and CPM for project risk analysis.
- **Input Schema:**
  - `project_network`: List of tasks (id, name, predecessors)
  - `risk_factors`: List of risk factors (task_id, mean, stddev)
  - `num_simulations`: Number of Monte Carlo runs
  - `objective`: "estimate_risk"
- **How it works:**
  1. Simulates project durations under uncertainty.
  2. Computes risk profile (mean, stddev, percentiles, histogram).
- **Sample MCP Payload:**
```json
{
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
}
```

---

## Request Processing Flow
1. **Request Received:**
   - The service receives a POST request at one of its endpoints.
2. **Input Validation:**
   - Uses Pydantic models to validate and parse the input JSON.
3. **Model Construction:**
   - For `/solve`, constructs the LP/MIP model from the input.
   - For specialized endpoints, constructs the domain model from objects.
4. **Solving:**
   - Uses Google OR-Tools (GLOP for LP, SCIP for MIP/VRP, CP-SAT for scheduling) or NumPy for simulation.
5. **Solution Extraction:**
   - Extracts variable values, assignments, sequences, and objective value.
6. **Response:**
   - Returns a JSON response with status, solution, and any errors.

---

## Deep Dive: How Solutions Are Generated
- **LP/MIP:**
  - Variables and constraints are parsed from the input and mapped to OR-Tools objects.
  - The solver optimizes the objective and returns variable values.
- **Vehicle Assignment:**
  - Assignment variables represent which vehicle serves which task.
  - Sequencing variables represent the order of tasks for each vehicle.
  - Constraints ensure each task is served, vehicle capacities are respected, and time windows are met.
  - The solver finds the optimal set of assignments and sequences to minimize total distance.
- **Labor Scheduling, Equipment Allocation, Material Delivery, Risk Simulation:**
  - Each endpoint uses a specialized model and solver (CP-SAT, MIP, VRPTW, Monte Carlo+CPM) to generate solutions tailored to the domain.

---

## Error Handling
- Returns detailed error messages for infeasible, unbounded, or malformed problems.
- Uses Pydantic validation for input errors.

---

## Extensibility
- New endpoints can be added for other domains (e.g., workforce scheduling, maintenance, labor scheduling, equipment allocation, material delivery, risk simulation).
- The generic `/solve` endpoint supports any LP/MIP that can be expressed in the input schema.

---

## Example Usage
- See `how-to.md` for sample payloads and curl commands.

---

## Endpoint Summary Table

| Endpoint                                 | Purpose                                      | Sample Usage (see how-to.md)         |
|------------------------------------------|----------------------------------------------|--------------------------------------|
| /solve                                   | Generic LP/MIP solver                        | [Generic LP/MIP](how-to.md#example-usage) |
| /solve/vehicle-assignment                | Vehicle routing/assignment                   | [Vehicle Assignment](how-to.md#example-usage) |
| /solve/labor-scheduling                  | Labor scheduling (CP-SAT)                    | [Labor Scheduling](how-to.md#example-labor-scheduling) |
| /solve/equipment-allocation              | Equipment allocation (MIP)                   | [Equipment Allocation](how-to.md#example-equipment-allocation) |
| /solve/material-delivery-planning        | Material delivery planning (VRPTW)           | [Material Delivery Planning](how-to.md#example-material-delivery-planning) |
| /solve/risk-simulation                   | Risk simulation (Monte Carlo + CPM)          | [Risk Simulation](how-to.md#example-risk-simulation) |

> **Note:** Sample payloads and curl commands for all endpoints are available in [how-to.md](how-to.md). 