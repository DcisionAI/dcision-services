from typing import Dict, Any, List
from ortools.linear_solver import pywraplp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from .templates import (
    VehicleAssignmentRequest, FleetMixRequest, MaintenanceScheduleRequest,
    FuelOptimizationRequest, EmployeeScheduleRequest, TaskAssignmentRequest,
    BreakScheduleRequest, LaborCostRequest, WorkforceCapacityRequest,
    ShiftCoverageRequest
)
from datetime import datetime

class SolverService:
    def __init__(self):
        self.solvers = {
            "lp": self._solve_lp,
            "mip": self._solve_mip,
            "cp": self._solve_cp,
            "vrp": self._solve_vrp,
            "vap": self._solve_vehicle_assignment,
            "fleet_mix": self._solve_fleet_mix,
            "maintenance": self._solve_maintenance,
            "fuel": self._solve_fuel,
            "employee_schedule": self._solve_employee_schedule,
            "task_assignment": self._solve_task_assignment,
            "break_schedule": self._solve_break_schedule,
            "labor_cost": self._solve_labor_cost,
            "workforce_capacity": self._solve_workforce_capacity,
            "shift_coverage": self._solve_shift_coverage
        }

    def solve(self, data: Dict[str, Any]) -> Dict[str, Any]:
        problem_type = data.get("type")
        if problem_type not in self.solvers:
            raise ValueError(f"Unsupported problem type: {problem_type}")
        
        try:
            return self.solvers[problem_type](data)
        except Exception as e:
            raise Exception(f"Failed to solve {problem_type}: {str(e)}")

    def _solve_lp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        solver = pywraplp.Solver.CreateSolver('GLOP')
        if not solver:
            raise Exception("Failed to create solver")
        
        # Create variables
        variables = {}
        for var in data["variables"]:
            name = var["name"]
            lower_bound = var.get("lower_bound", float('-inf'))
            upper_bound = var.get("upper_bound", float('inf'))
            variables[name] = solver.NumVar(lower_bound, upper_bound, name)
        
        # Add constraints
        for constraint in data.get("constraints", []):
            expr = constraint["expression"]
            operator = constraint["operator"]
            rhs = constraint["rhs"]
            
            # Parse the expression (this is a simplified version)
            # In a real implementation, you would need a proper expression parser
            terms = expr.split('+')
            linear_expr = solver.Sum([
                float(term.strip().split('*')[0]) * variables[term.strip().split('*')[1]]
                if '*' in term else variables[term.strip()]
                for term in terms
            ])
            
            if operator == "<=":
                solver.Add(linear_expr <= rhs)
            elif operator == ">=":
                solver.Add(linear_expr >= rhs)
            elif operator == "=":
                solver.Add(linear_expr == rhs)
        
        # Set objective
        objective = data["objective"]
        expr = objective["expression"]
        terms = expr.split('+')
        linear_expr = solver.Sum([
            float(term.strip().split('*')[0]) * variables[term.strip().split('*')[1]]
            if '*' in term else variables[term.strip()]
            for term in terms
        ])
        
        if objective["type"] == "minimize":
            solver.Minimize(linear_expr)
        else:
            solver.Maximize(linear_expr)
        
        # Solve
        status = solver.Solve()
        
        # Return solution
        if status == pywraplp.Solver.OPTIMAL:
            return {
                "status": "OPTIMAL",
                "solution": {name: var.solution_value() for name, var in variables.items()},
                "objective_value": solver.Objective().Value(),
                "solve_time": solver.WallTime() / 1000,  # Convert to seconds
                "iterations": solver.Iterations()
            }
        elif status == pywraplp.Solver.FEASIBLE:
            return {
                "status": "FEASIBLE",
                "solution": {name: var.solution_value() for name, var in variables.items()},
                "objective_value": solver.Objective().Value(),
                "solve_time": solver.WallTime() / 1000,
                "iterations": solver.Iterations()
            }
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Problem is infeasible")
        elif status == pywraplp.Solver.UNBOUNDED:
            raise Exception("Problem is unbounded")
        else:
            raise Exception("Failed to solve lp")

    def _solve_mip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        solver = pywraplp.Solver.CreateSolver('SCIP')
        # Implementation for mixed integer programming
        return {"status": "success", "solution": {}}

    def _solve_cp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        solver = pywrapcp.Solver('CP')
        # Implementation for constraint programming
        return {"status": "success", "solution": {}}

    def _solve_vrp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Existing VRP implementation
        return {"status": "success", "solution": {}}

    def _solve_vehicle_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = VehicleAssignmentRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        assignments = {}
        sequence = {}  # Variables for sequencing tasks
        for v in request.vehicles:
            for t1 in request.tasks:
                assignments[(v.id, t1.id)] = solver.BoolVar(f'x_{v.id}_{t1.id}')
                for t2 in request.tasks:
                    if t1.id != t2.id:
                        sequence[(v.id, t1.id, t2.id)] = solver.BoolVar(f'y_{v.id}_{t1.id}_{t2.id}')
        
        # Add constraints
        # Each task must be assigned to exactly one vehicle
        for t in request.tasks:
            solver.Add(sum(assignments[(v.id, t.id)] for v in request.vehicles) == 1)
        
        # Vehicle capacity constraints
        for v in request.vehicles:
            solver.Add(sum(assignments[(v.id, t.id)] * t.duration for t in request.tasks) <= v.capacity)
        
        # Sequence constraints
        for v in request.vehicles:
            for t1 in request.tasks:
                # Flow conservation: if a task is assigned to a vehicle, it must have exactly one next task
                solver.Add(sum(sequence[(v.id, t1.id, t2.id)] for t2 in request.tasks if t1.id != t2.id) == assignments[(v.id, t1.id)])
                # Flow conservation: if a task is assigned to a vehicle, it must have exactly one previous task
                solver.Add(sum(sequence[(v.id, t2.id, t1.id)] for t2 in request.tasks if t1.id != t2.id) == assignments[(v.id, t1.id)])
        
        # Time window constraints
        M = 100000  # Big M constant
        arrival_time = {}
        for v in request.vehicles:
            for t in request.tasks:
                arrival_time[(v.id, t.id)] = solver.NumVar(0, M, f't_{v.id}_{t.id}')
                # Time window constraints
                solver.Add(arrival_time[(v.id, t.id)] >= t.time_window[0] * assignments[(v.id, t.id)])
                solver.Add(arrival_time[(v.id, t.id)] <= t.time_window[1] * assignments[(v.id, t.id)] + M * (1 - assignments[(v.id, t.id)]))
        
        # Precedence constraints for arrival times
        for v in request.vehicles:
            for t1 in request.tasks:
                for t2 in request.tasks:
                    if t1.id != t2.id:
                        # If t1 is followed by t2, ensure arrival times are consistent
                        solver.Add(arrival_time[(v.id, t2.id)] >= arrival_time[(v.id, t1.id)] + t1.duration + 
                                request.distance_matrix[t1.location.id][t2.location.id] - M * (1 - sequence[(v.id, t1.id, t2.id)]))
        
        # Objective: minimize total distance
        objective = solver.Objective()
        for v in request.vehicles:
            for t1 in request.tasks:
                for t2 in request.tasks:
                    if t1.id != t2.id:
                        distance = request.distance_matrix[t1.location.id][t2.location.id]
                        objective.SetCoefficient(sequence[(v.id, t1.id, t2.id)], distance)
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "assignments": [],
                "sequence": [],
                "total_distance": objective.Value()
            }
            for v in request.vehicles:
                vehicle_tasks = []
                for t in request.tasks:
                    if assignments[(v.id, t.id)].solution_value() > 0.5:
                        vehicle_tasks.append({
                            "vehicle_id": v.id,
                            "task_id": t.id,
                            "arrival_time": arrival_time[(v.id, t.id)].solution_value()
                        })
                        # Find the sequence
                        for t2 in request.tasks:
                            if t.id != t2.id and sequence[(v.id, t.id, t2.id)].solution_value() > 0.5:
                                solution["sequence"].append({
                                    "vehicle_id": v.id,
                                    "from_task": t.id,
                                    "to_task": t2.id
                                })
                solution["assignments"].extend(sorted(vehicle_tasks, key=lambda x: x["arrival_time"]))
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_fleet_mix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = FleetMixRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        vehicle_counts = {}
        for v_type in request.vehicle_types:
            vehicle_counts[v_type["id"]] = solver.IntVar(0, solver.infinity(), f'x_{v_type["id"]}')
        
        # Add constraints
        # Budget constraint
        solver.Add(sum(vehicle_counts[v["id"]] * v["cost"] for v in request.vehicle_types) <= request.constraints["budget"])
        
        # Vehicle count constraints
        solver.Add(sum(vehicle_counts.values()) >= request.constraints["min_vehicles"])
        solver.Add(sum(vehicle_counts.values()) <= request.constraints["max_vehicles"])
        
        # Demand coverage constraints
        for t, demand in enumerate(request.demand_forecast):
            solver.Add(sum(vehicle_counts[v["id"]] * v["capacity"] for v in request.vehicle_types) >= demand)
        
        # Objective: minimize total cost
        objective = solver.Objective()
        for v_type in request.vehicle_types:
            objective.SetCoefficient(vehicle_counts[v_type["id"]], v_type["cost"])
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "vehicle_counts": {v_id: int(vehicle_counts[v_id].solution_value()) for v_id in vehicle_counts},
                "total_cost": objective.Value()
            }
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_maintenance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = MaintenanceScheduleRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        maintenance_schedule = {}
        for v in request.vehicles:
            for m in request.maintenance_tasks:
                for t in range(request.time_horizon):
                    maintenance_schedule[(v.id, m.id, t)] = solver.BoolVar(f'x_{v.id}_{m.id}_{t}')
        
        # Add constraints
        # Each maintenance task must be scheduled exactly once
        for m in request.maintenance_tasks:
            solver.Add(sum(maintenance_schedule[(v.id, m.id, t)] for t in range(request.time_horizon)) == 1)
        
        # Maintenance delay constraints
        for v in request.vehicles:
            for m in request.maintenance_tasks:
                if m.vehicle_id == v.id:
                    solver.Add(sum(t * maintenance_schedule[(v.id, m.id, t)] for t in range(request.time_horizon)) <= v.maintenance_interval + request.constraints["max_maintenance_delay"])
        
        # Facility capacity constraints
        for f in request.maintenance_facilities:
            for t in range(request.time_horizon):
                solver.Add(sum(maintenance_schedule[(v.id, m.id, t)] for v in request.vehicles for m in request.maintenance_tasks) <= request.constraints["facility_capacity"][f.id])
        
        # Objective: minimize total delay
        objective = solver.Objective()
        for v in request.vehicles:
            for m in request.maintenance_tasks:
                if m.vehicle_id == v.id:
                    for t in range(request.time_horizon):
                        delay = max(0, t - v.maintenance_interval)
                        objective.SetCoefficient(maintenance_schedule[(v.id, m.id, t)], delay)
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "schedule": [],
                "total_delay": objective.Value()
            }
            for v in request.vehicles:
                for m in request.maintenance_tasks:
                    for t in range(request.time_horizon):
                        if maintenance_schedule[(v.id, m.id, t)].solution_value() > 0.5:
                            solution["schedule"].append({
                                "vehicle_id": v.id,
                                "maintenance_id": m.id,
                                "time": t
                            })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_fuel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = FuelOptimizationRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        refuel_stops = {}
        for v in request.vehicles:
            for r in request.routes:
                for s in request.fuel_stations:
                    refuel_stops[(v.id, r[0].id, s.id)] = solver.BoolVar(f'x_{v.id}_{r[0].id}_{s.id}')
        
        # Add constraints
        # Fuel level constraints
        for v in request.vehicles:
            for r in request.routes:
                total_distance = sum(request.distance_matrix[r[i].id][r[i+1].id] for i in range(len(r)-1))
                fuel_consumption = total_distance / v.fuel_efficiency
                solver.Add(sum(refuel_stops[(v.id, r[0].id, s.id)] for s in request.fuel_stations) * request.constraints["max_fuel_level"] >= fuel_consumption)
        
        # Objective: minimize total fuel cost
        objective = solver.Objective()
        for v in request.vehicles:
            for r in request.routes:
                for s in request.fuel_stations:
                    objective.SetCoefficient(refuel_stops[(v.id, r[0].id, s.id)], request.fuel_prices[s.id])
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "refuel_stops": [],
                "total_cost": objective.Value()
            }
            for v in request.vehicles:
                for r in request.routes:
                    for s in request.fuel_stations:
                        if refuel_stops[(v.id, r[0].id, s.id)].solution_value() > 0.5:
                            solution["refuel_stops"].append({
                                "vehicle_id": v.id,
                                "route_id": r[0].id,
                                "station_id": s.id
                            })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_employee_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = EmployeeScheduleRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        schedule = {}
        for e in request.employees:
            for t in request.tasks:
                for h in range(request.time_horizon):
                    schedule[(e.id, t.id, h)] = solver.BoolVar(f'x_{e.id}_{t.id}_{h}')
        
        # Add constraints
        # Each task must be assigned to exactly one employee
        for t in request.tasks:
            solver.Add(sum(schedule[(e.id, t.id, h)] for e in request.employees for h in range(request.time_horizon)) == 1)
        
        # Employee working hours constraints
        for e in request.employees:
            solver.Add(sum(schedule[(e.id, t.id, h)] * t.duration for t in request.tasks for h in range(request.time_horizon)) <= e.max_hours)
        
        # Skill requirements
        for t in request.tasks:
            for e in request.employees:
                if not all(skill in e.skills for skill in t.required_skills):
                    solver.Add(sum(schedule[(e.id, t.id, h)] for h in range(request.time_horizon)) == 0)
        
        # Objective: minimize total cost
        objective = solver.Objective()
        for e in request.employees:
            for t in request.tasks:
                for h in range(request.time_horizon):
                    objective.SetCoefficient(schedule[(e.id, t.id, h)], e.hourly_rate * t.duration)
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "schedule": [],
                "total_cost": objective.Value()
            }
            for e in request.employees:
                for t in request.tasks:
                    for h in range(request.time_horizon):
                        if schedule[(e.id, t.id, h)].solution_value() > 0.5:
                            solution["schedule"].append({
                                "employee_id": e.id,
                                "task_id": t.id,
                                "hour": h
                            })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_task_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = TaskAssignmentRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        assignments = {}
        for e in request.employees:
            for t in request.tasks:
                assignments[(e.id, t.id)] = solver.BoolVar(f'x_{e.id}_{t.id}')
        
        # Add constraints
        # Each task must be assigned to exactly one employee
        for t in request.tasks:
            solver.Add(sum(assignments[(e.id, t.id)] for e in request.employees) == 1)
        
        # Maximum tasks per employee
        for e in request.employees:
            solver.Add(sum(assignments[(e.id, t.id)] for t in request.tasks) <= request.constraints["max_tasks_per_employee"])
        
        # Skill requirements
        for t in request.tasks:
            for e in request.employees:
                if not all(skill in e.skills for skill in t.required_skills):
                    solver.Add(assignments[(e.id, t.id)] == 0)
        
        # Objective: maximize task priority
        objective = solver.Objective()
        for e in request.employees:
            for t in request.tasks:
                objective.SetCoefficient(assignments[(e.id, t.id)], t.priority)
        objective.SetMaximization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "assignments": [],
                "total_priority": objective.Value()
            }
            for e in request.employees:
                for t in request.tasks:
                    if assignments[(e.id, t.id)].solution_value() > 0.5:
                        solution["assignments"].append({
                            "employee_id": e.id,
                            "task_id": t.id
                        })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_break_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = BreakScheduleRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        breaks = {}
        for e in request.employees:
            for t in range(request.time_horizon):
                breaks[(e.id, t)] = solver.BoolVar(f'x_{e.id}_{t}')
        
        # Add constraints
        # Break duration
        for e in request.employees:
            solver.Add(sum(breaks[(e.id, t)] for t in range(request.time_horizon)) == request.constraints["break_duration"])
        
        # Minimum work before break
        for e in request.employees:
            for t in range(request.time_horizon):
                if t < request.constraints["min_work_before_break"]:
                    solver.Add(breaks[(e.id, t)] == 0)
        
        # Maximum work before break
        for e in request.employees:
            for t in range(request.time_horizon):
                if t > request.constraints["max_work_before_break"]:
                    solver.Add(sum(breaks[(e.id, t2)] for t2 in range(t-request.constraints["max_work_before_break"], t)) >= 1)
        
        # Objective: minimize deviation from preferred break times
        objective = solver.Objective()
        for e in request.employees:
            for t in range(request.time_horizon):
                deviation = min(abs(t - p["time"]) for p in request.constraints["preferred_break_times"] if p["employee_id"] == e.id)
                objective.SetCoefficient(breaks[(e.id, t)], deviation)
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "breaks": [],
                "total_deviation": objective.Value()
            }
            for e in request.employees:
                for t in range(request.time_horizon):
                    if breaks[(e.id, t)].solution_value() > 0.5:
                        solution["breaks"].append({
                            "employee_id": e.id,
                            "time": t
                        })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_labor_cost(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = LaborCostRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        assignments = {}
        for e in request.employees:
            for t in request.tasks:
                assignments[(e.id, t.id)] = solver.BoolVar(f'x_{e.id}_{t.id}')
        
        # Add constraints
        # Budget constraint
        solver.Add(sum(assignments[(e.id, t.id)] * e.hourly_rate * t.duration for e in request.employees for t in request.tasks) <= request.constraints["budget"])
        
        # Minimum coverage
        for skill, count in request.constraints["min_coverage"].items():
            solver.Add(sum(assignments[(e.id, t.id)] for e in request.employees for t in request.tasks if skill in e.skills) >= count)
        
        # Maximum overtime
        for e in request.employees:
            solver.Add(sum(assignments[(e.id, t.id)] * t.duration for t in request.tasks) <= e.max_hours + request.constraints["max_overtime"])
        
        # Objective: maximize task completion
        objective = solver.Objective()
        for e in request.employees:
            for t in request.tasks:
                objective.SetCoefficient(assignments[(e.id, t.id)], 1)
        objective.SetMaximization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "assignments": [],
                "total_tasks": objective.Value()
            }
            for e in request.employees:
                for t in request.tasks:
                    if assignments[(e.id, t.id)].solution_value() > 0.5:
                        solution["assignments"].append({
                            "employee_id": e.id,
                            "task_id": t.id
                        })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_workforce_capacity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = WorkforceCapacityRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        hiring = {}
        for skill in request.constraints["skill_requirements"].keys():
            hiring[skill] = solver.IntVar(0, solver.infinity(), f'h_{skill}')
        
        # Add constraints
        # Demand coverage
        for t, demand in enumerate(request.demand_forecast):
            solver.Add(sum(hiring[skill] for skill in request.constraints["skill_requirements"].keys()) >= demand)
        
        # Maximum hours per employee
        for skill in request.constraints["skill_requirements"].keys():
            solver.Add(hiring[skill] * request.constraints["max_hours_per_employee"] >= sum(request.demand_forecast))
        
        # Objective: minimize hiring costs
        objective = solver.Objective()
        for skill in request.constraints["skill_requirements"].keys():
            objective.SetCoefficient(hiring[skill], request.constraints["hiring_costs"][skill])
        objective.SetMinimization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "hiring": {skill: int(hiring[skill].solution_value()) for skill in hiring},
                "total_cost": objective.Value()
            }
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def _solve_shift_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = ShiftCoverageRequest(**data)
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        assignments = {}
        for e in request.employees:
            for s in request.shifts:
                assignments[(e.id, s["id"])] = solver.BoolVar(f'x_{e.id}_{s["id"]}')
        
        # Add constraints
        # Minimum employees per shift
        for s in request.shifts:
            solver.Add(sum(assignments[(e.id, s["id"])] for e in request.employees) >= request.constraints["min_employees_per_shift"][s["type"]])
        
        # Maximum consecutive shifts
        for e in request.employees:
            for t in range(request.time_horizon - request.constraints["max_consecutive_shifts"]):
                solver.Add(sum(assignments[(e.id, s["id"])] for s in request.shifts if s["time"] in range(t, t + request.constraints["max_consecutive_shifts"])) <= request.constraints["max_consecutive_shifts"])
        
        # Minimum rest between shifts
        for e in request.employees:
            for t in range(request.time_horizon):
                solver.Add(sum(assignments[(e.id, s["id"])] for s in request.shifts if s["time"] in range(t, t + request.constraints["min_rest_between_shifts"])) <= 1)
        
        # Objective: maximize shift coverage
        objective = solver.Objective()
        for e in request.employees:
            for s in request.shifts:
                objective.SetCoefficient(assignments[(e.id, s["id"])], 1)
        objective.SetMaximization()
        
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            solution = {
                "assignments": [],
                "total_coverage": objective.Value()
            }
            for e in request.employees:
                for s in request.shifts:
                    if assignments[(e.id, s["id"])].solution_value() > 0.5:
                        solution["assignments"].append({
                            "employee_id": e.id,
                            "shift_id": s["id"]
                        })
            return {"status": "success", "solution": solution}
        else:
            return {"status": "failed", "error": "No optimal solution found"}

    def build_model(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Build an optimization model from the request."""
        try:
            # Validate the model structure
            if not all(key in request for key in ["variables", "constraints", "objective"]):
                raise ValueError("Missing required model components")
            
            # Create the model representation
            model = {
                "variables": request["variables"],
                "constraints": request["constraints"],
                "objective": request["objective"],
                "parameters": {},  # Initialize parameters as empty dict
                "metadata": {
                    "name": request.get("name", "Unnamed Model"),
                    "description": request.get("description", ""),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            return model
        except Exception as e:
            raise Exception(f"Failed to build model: {str(e)}")

    def run_model(self, model: Dict[str, Any], run_request: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run an optimization model with optional parameters."""
        try:
            # Ensure model has required fields
            if not isinstance(model, dict):
                raise ValueError("Model must be a dictionary")
            
            if not all(key in model for key in ["variables", "constraints", "objective"]):
                raise ValueError("Model missing required components: variables, constraints, or objective")
            
            # Validate variables
            if not isinstance(model["variables"], list):
                raise ValueError("Variables must be a list")
            
            # Validate constraints
            if not isinstance(model["constraints"], list):
                raise ValueError("Constraints must be a list")
            
            # Validate objective
            if not isinstance(model["objective"], dict):
                raise ValueError("Objective must be a dictionary")
            
            # Initialize parameters if not present
            if "parameters" not in model:
                model["parameters"] = {}
            
            # Update model parameters if provided
            if run_request and isinstance(run_request, dict) and "parameters" in run_request:
                model["parameters"].update(run_request["parameters"])
            
            # Determine the appropriate solver based on variable types
            variable_types = {v["type"] for v in model["variables"]}
            if "binary" in variable_types or "integer" in variable_types:
                solver_type = "mip"
            else:
                solver_type = "lp"
            
            # Prepare the data for the solver
            solver_data = {
                "type": solver_type,
                "variables": model["variables"],
                "constraints": model["constraints"],
                "objective": model["objective"],
                "parameters": model["parameters"]
            }
            
            # Run the solver
            return self.solve(solver_data)
        except Exception as e:
            raise Exception(f"Failed to run model: {str(e)}") 