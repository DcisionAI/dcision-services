from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.core.solver import SolverService
from src.core.model_store import model_store, ModelStore
from src.api.models import ModelBuildRequest, ModelRunRequest
from src.core.templates import (
    VehicleAssignmentRequest, FleetMixRequest, MaintenanceScheduleRequest,
    FuelOptimizationRequest, EmployeeScheduleRequest, TaskAssignmentRequest,
    BreakScheduleRequest, LaborCostRequest, WorkforceCapacityRequest,
    ShiftCoverageRequest
)
import uuid
from datetime import datetime

app = FastAPI()
solver_service = SolverService()
model_store = ModelStore()

@app.post("/build")
def build_model(request: Dict[str, Any]):
    try:
        model = solver_service.build_model(request)
        model_id = str(uuid.uuid4())
        model_store.store_model(model_id, model)
        return {"model_id": model_id, "status": "built"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/run/{model_id}")
def run_model(model_id: str, run_request: Dict[str, Any] = None):
    try:
        model = model_store.get_model(model_id)
        result = solver_service.run_model(model, run_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve")
def solve_model(request: Dict[str, Any]):
    """Solve a model directly without storing it."""
    try:
        # Build the model
        model = solver_service.build_model(request)
        # Run the model immediately
        result = solver_service.run_model(model)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/vehicle-assignment")
def solve_vehicle_assignment(request: VehicleAssignmentRequest):
    try:
        result = solver_service.solve({
            "type": "vap",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/fleet-mix")
def solve_fleet_mix(request: FleetMixRequest):
    try:
        result = solver_service.solve({
            "type": "fleet_mix",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/maintenance")
async def solve_maintenance(request: MaintenanceScheduleRequest):
    try:
        result = await solver_service.solve({
            "type": "maintenance",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/fuel")
async def solve_fuel(request: FuelOptimizationRequest):
    try:
        result = await solver_service.solve({
            "type": "fuel",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/employee-schedule")
async def solve_employee_schedule(request: EmployeeScheduleRequest):
    try:
        result = await solver_service.solve({
            "type": "employee_schedule",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/task-assignment")
async def solve_task_assignment(request: TaskAssignmentRequest):
    try:
        result = await solver_service.solve({
            "type": "task_assignment",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/break-schedule")
async def solve_break_schedule(request: BreakScheduleRequest):
    try:
        result = await solver_service.solve({
            "type": "break_schedule",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/labor-cost")
async def solve_labor_cost(request: LaborCostRequest):
    try:
        result = await solver_service.solve({
            "type": "labor_cost",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/workforce-capacity")
async def solve_workforce_capacity(request: WorkforceCapacityRequest):
    try:
        result = await solver_service.solve({
            "type": "workforce_capacity",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/shift-coverage")
async def solve_shift_coverage(request: ShiftCoverageRequest):
    try:
        result = await solver_service.solve({
            "type": "shift_coverage",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 