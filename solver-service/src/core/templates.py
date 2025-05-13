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