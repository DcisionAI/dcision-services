from typing import Dict, Any, List
from pydantic import BaseModel

class Location(BaseModel):
    id: int
    latitude: float
    longitude: float
    name: str = ""

class Vehicle(BaseModel):
    id: int
    type: str
    capacity: float
    operating_cost: float
    maintenance_interval: int
    fuel_efficiency: float

class Driver(BaseModel):
    id: int
    name: str
    skills: List[str]
    max_hours: float
    hourly_rate: float
    availability: List[Dict[str, Any]]

class Task(BaseModel):
    id: int
    location: Location
    duration: float
    required_skills: List[str]
    priority: int
    time_window: List[float]

class MaintenanceTask(BaseModel):
    id: int
    vehicle_id: int
    type: str
    duration: float
    required_parts: List[str]
    priority: int

# FleetOps Templates
class VehicleAssignmentRequest(BaseModel):
    vehicles: List[Vehicle]
    tasks: List[Task]
    locations: List[Location]
    distance_matrix: List[List[float]]
    constraints: Dict[str, Any] = {
        "max_distance": float,
        "max_working_hours": float,
        "vehicle_availability": List[Dict[str, Any]]
    }

class FleetMixRequest(BaseModel):
    vehicle_types: List[Dict[str, Any]]
    demand_forecast: List[float]
    cost_parameters: Dict[str, float]
    constraints: Dict[str, Any] = {
        "budget": float,
        "min_vehicles": int,
        "max_vehicles": int
    }

class MaintenanceScheduleRequest(BaseModel):
    vehicles: List[Vehicle]
    maintenance_tasks: List[MaintenanceTask]
    maintenance_facilities: List[Location]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "max_maintenance_delay": int,
        "facility_capacity": List[int],
        "working_hours": List[Dict[str, Any]]
    }

class FuelOptimizationRequest(BaseModel):
    vehicles: List[Vehicle]
    routes: List[List[Location]]
    fuel_stations: List[Location]
    fuel_prices: List[float]
    constraints: Dict[str, Any] = {
        "min_fuel_level": float,
        "max_fuel_level": float,
        "fuel_consumption_rate": float
    }

# Workforce Management Templates
class EmployeeScheduleRequest(BaseModel):
    employees: List[Driver]
    tasks: List[Task]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "min_rest_hours": float,
        "max_consecutive_hours": float,
        "required_breaks": List[Dict[str, Any]],
        "skill_requirements": Dict[str, List[str]]
    }

class TaskAssignmentRequest(BaseModel):
    employees: List[Driver]
    tasks: List[Task]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "max_tasks_per_employee": int,
        "min_rest_between_tasks": float,
        "skill_requirements": Dict[str, List[str]],
        "preferred_assignments": List[Dict[str, Any]]
    }

class BreakScheduleRequest(BaseModel):
    employees: List[Driver]
    tasks: List[Task]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "break_duration": float,
        "min_work_before_break": float,
        "max_work_before_break": float,
        "preferred_break_times": List[Dict[str, Any]]
    }

class LaborCostRequest(BaseModel):
    employees: List[Driver]
    tasks: List[Task]
    time_horizon: int
    cost_parameters: Dict[str, float]
    constraints: Dict[str, Any] = {
        "budget": float,
        "min_coverage": Dict[str, int],
        "max_overtime": float,
        "skill_requirements": Dict[str, List[str]]
    }

class WorkforceCapacityRequest(BaseModel):
    employees: List[Driver]
    demand_forecast: List[float]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "min_coverage": Dict[str, int],
        "max_hours_per_employee": float,
        "skill_requirements": Dict[str, List[str]],
        "hiring_costs": Dict[str, float]
    }

class ShiftCoverageRequest(BaseModel):
    employees: List[Driver]
    shifts: List[Dict[str, Any]]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "min_employees_per_shift": Dict[str, int],
        "max_consecutive_shifts": int,
        "min_rest_between_shifts": float,
        "skill_requirements": Dict[str, List[str]]
    }

# --- New World-Class OR Models ---

class LaborSchedulingRequest(BaseModel):
    employees: List[Driver]
    shifts: List[Dict[str, Any]]
    time_horizon: int
    constraints: Dict[str, Any] = {
        "min_rest_hours": float,
        "max_consecutive_hours": float,
        "required_breaks": List[Dict[str, Any]],
        "skill_requirements": Dict[str, List[str]],
        "coverage_requirements": Dict[str, int]
    }
    objective: str = "minimize_cost"  # or "maximize_coverage"

class EquipmentAllocationRequest(BaseModel):
    equipment: List[Dict[str, Any]]  # id, type, capacity, cost
    tasks: List[Task]
    locations: List[Location]
    cost_matrix: List[List[float]]
    constraints: Dict[str, Any] = {
        "max_equipment_per_location": int,
        "min_tasks_per_equipment": int,
        "assignment_restrictions": List[Dict[str, Any]]
    }
    objective: str = "minimize_total_cost"

class MaterialDeliveryPlanningRequest(BaseModel):
    vehicles: List[Vehicle]
    deliveries: List[Task]  # Each task is a delivery
    locations: List[Location]
    time_windows: List[List[float]]
    distance_matrix: List[List[float]]
    constraints: Dict[str, Any] = {
        "vehicle_capacity": float,
        "max_route_time": float,
        "delivery_time_windows": List[List[float]]
    }
    objective: str = "minimize_total_distance"

class RiskSimulationRequest(BaseModel):
    project_network: List[Dict[str, Any]]  # CPM network: tasks, dependencies, durations
    risk_factors: List[Dict[str, Any]]  # e.g., distributions for durations
    num_simulations: int = 1000
    objective: str = "estimate_risk"

# --- Construction Optimization Use Cases ---
class CrewAllocationRequest(BaseModel):
    crews: List[Dict[str, Any]]       # list of workers with skills, availability
    sites: List[Dict[str, Any]]       # work sites with requirements
    tasks: List[Dict[str, Any]]       # tasks to assign per site
    shifts: List[Dict[str, Any]]      # shift definitions (start, end, break rules)
    union_rules: List[Dict[str, Any]] # contractual and legal constraints
    priorities: Dict[int, int]        # site_id -> priority weight

class EquipmentResourcePlanningRequest(BaseModel):
    equipment: List[Dict[str, Any]]   # high-value assets with capacities
    projects: List[Dict[str, Any]]    # project sites and timelines
    tasks: List[Dict[str, Any]]       # equipment usage tasks per site
    time_horizon: int                 # planning horizon in days
    move_times: List[List[float]]     # transport/setup times matrix
    constraints: Dict[str, Any]       # budget, max moves, etc.

class SubcontractorScheduleRequest(BaseModel):
    subcontractors: List[Dict[str, Any]]  # subcontractor entities
    tasks: List[Dict[str, Any]]           # project tasks with dependencies
    contracts: List[Dict[str, Any]]       # time windows and scopes
    time_horizon: int                     # overall schedule horizon

class MaterialDeliveryOptimizationRequest(BaseModel):
    deliveries: List[Dict[str, Any]]      # material drop-offs with qty, time windows
    vehicles: List[Dict[str, Any]]        # delivery vehicles
    storage: List[Dict[str, Any]]         # storage facilities with capacity
    distance_matrix: List[List[float]]    # travel distances between locations
    constraints: Dict[str, Any]           # inventory and site constraints

class PortfolioBalancingRequest(BaseModel):
    sites: List[Dict[str, Any]]           # active projects with deadlines/budgets
    resources: List[Dict[str, Any]]       # labor/equipment pools
    weights: Dict[int, float]             # site_id -> priority or risk weight
    constraints: Dict[str, Any]           # min/max allocations, budgets

class ChangeOrderImpactRequest(BaseModel):
    original_plan: Dict[str, Any]         # prior schedule or resource plan
    change_orders: List[Dict[str, Any]]   # new scope changes
    num_simulations: int = 100            # Monte Carlo runs for impact

class CompliancePlanningRequest(BaseModel):
    tasks: List[Dict[str, Any]]           # scheduled work tasks
    blackout_windows: List[List[float]]   # forbidden time intervals [start,end]
    constraints: Dict[str, Any]           # permit rules, noise curfews, etc.