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
    ShiftCoverageRequest,
    LaborSchedulingRequest, EquipmentAllocationRequest, MaterialDeliveryPlanningRequest,
    RiskSimulationRequest,
    CrewAllocationRequest, EquipmentResourcePlanningRequest,
    SubcontractorScheduleRequest, MaterialDeliveryOptimizationRequest,
    PortfolioBalancingRequest, ChangeOrderImpactRequest,
    CompliancePlanningRequest
)
from src.api.models import (
    ModelBuildRequest, ModelRunRequest,
    ExplainRequest, ExplainResponse, SectionExplanation,
    FlowItem, FlowsResponse
)
import os, json
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
except ImportError:
    # Dummy OpenAI client for explain endpoint stubbing
    class DummyChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            raise RuntimeError("OpenAI SDK not available")
    class openai:
        ChatCompletion = DummyChatCompletion
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://platform.dcisionai.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
solver_service = SolverService()
model_store = ModelStore()
# Static metadata for each solver flow:
# - description: human-readable description of expected model format
# - mcpModelSchema: keys and types expected in the MCP model payload
FLOW_DESCRIPTIONS = {
    'crew_allocation': 'Allocate crews to tasks based on skills, availability, and labor rules',
    'equipment_resource_planning': 'Plan equipment usage tasks across sites and minimize equipment count',
    'subcontractor_scheduling': 'Schedule subcontractor tasks respecting dependencies',
    'material_delivery_optimization': 'Optimize material deliveries among vehicles under capacity',
    'portfolio_balancing': 'Balance resource allocations across multiple projects',
    'change_order_impact': 'Simulate schedule impact of change orders',
    'compliance_planning': 'Schedule tasks while respecting blackout windows and permit constraints',
    'vap': 'Vehicle assignment (VRP) solver',
    'fleet_mix': 'Optimize fleet composition',
    'maintenance': 'Schedule maintenance tasks for vehicles',
    'fuel': 'Optimize fuel stops and routing',
    'employee_schedule': 'Schedule employees to tasks and shifts',
    'task_assignment': 'Assign tasks to employees under constraints',
    'break_schedule': 'Plan employee break times',
    'labor_cost': 'Minimize labor cost subject to budget',
    'workforce_capacity': 'Match workforce capacity to demand forecasts',
    'shift_coverage': 'Allocate workforce to cover shifts',
    'labor_scheduling': 'Generate labor schedules across shifts'
}
FLOW_SCHEMAS = {
    'crew_allocation': {
        'crews': 'Array<{id:number, skills:string[], availability:[number,number][]}>',
        'tasks': 'Array<{id:number, site_id:number, required_skills:string[], duration:number}>',
        'shifts': 'Array<{id:number, start:number, end:number}>',
        'union_rules': 'Array<{max_work_hours_per_day:number}>',
        'priorities': '{[site_id:number]:number}'
    },
    'equipment_resource_planning': {
        'equipment': 'Array<{id:number, capacity:number}>',
        'tasks': 'Array<{id:number, time_window?:[number,number]}>',
        'projects': 'Array<any>',
        'time_horizon': 'number',
        'move_times': 'number[][]',
        'constraints': 'object'
    },
    'subcontractor_scheduling': {
        'tasks': 'Array<{id:number, duration:number, predecessors:number[]}>',
        'contracts': 'Array<any>',
        'time_horizon': 'number'
    },
    'material_delivery_optimization': {
        'vehicles': 'Array<{id:number, capacity:number}>',
        'deliveries': 'Array<{id:number, quantity:number}>',
        'storage': 'Array<any>',
        'distance_matrix': 'number[][]',
        'constraints': 'object'
    },
    'portfolio_balancing': {
        'sites': 'Array<{id:number}>',
        'resources': 'Array<{id:number, count:number}>',
        'weights': '{[site_id:number]:number}',
        'constraints': 'object'
    },
    'change_order_impact': {
        'original_plan': 'object',
        'change_orders': 'Array<{task_id:number, duration_delta:number}>',
        'num_simulations?': 'number'
    },
    'compliance_planning': {
        'tasks': 'Array<{id:number, duration:number}>',
        'blackout_windows': 'Array<[number,number]>',
        'constraints': 'object'
    }
}

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

@app.post("/solve/labor-scheduling")
def solve_labor_scheduling(request: LaborSchedulingRequest):
    try:
        result = solver_service.solve({
            "type": "labor_scheduling",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/equipment-allocation")
def solve_equipment_allocation(request: EquipmentAllocationRequest):
    try:
        result = solver_service.solve({
            "type": "equipment_allocation",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/material-delivery-planning")
def solve_material_delivery_planning(request: MaterialDeliveryPlanningRequest):
    try:
        result = solver_service.solve({
            "type": "material_delivery_planning",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/risk-simulation")
def solve_risk_simulation(request: RiskSimulationRequest):
    try:
        result = solver_service.solve({
            "type": "risk_simulation",
            **request.dict()
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Construction Optimization Solve Endpoints ---
@app.post("/solve/crew-allocation")
def solve_crew_allocation(request: CrewAllocationRequest):
    try:
        return solver_service.solve({"type": "crew_allocation", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/equipment-resource-planning")
def solve_equipment_resource_planning(request: EquipmentResourcePlanningRequest):
    try:
        return solver_service.solve({"type": "equipment_resource_planning", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/subcontractor-scheduling")
def solve_subcontractor_scheduling(request: SubcontractorScheduleRequest):
    try:
        return solver_service.solve({"type": "subcontractor_scheduling", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/material-delivery-optimization")
def solve_material_delivery_optimization(request: MaterialDeliveryOptimizationRequest):
    try:
        return solver_service.solve({"type": "material_delivery_optimization", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/portfolio-balancing")
def solve_portfolio_balancing(request: PortfolioBalancingRequest):
    try:
        return solver_service.solve({"type": "portfolio_balancing", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/change-order-impact")
def solve_change_order_impact(request: ChangeOrderImpactRequest):
    try:
        return solver_service.solve({"type": "change_order_impact", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/solve/compliance-planning")
def solve_compliance_planning(request: CompliancePlanningRequest):
    try:
        return solver_service.solve({"type": "compliance_planning", **request.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Explainability Endpoint ---
@app.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
    if openai is None:
        raise HTTPException(status_code=500, detail="OpenAI SDK not installed")
    # Build system and user prompts for the LLM
    system_prompt = (
        "You are an expert AI assistant specialized in explaining optimization solver outputs. "
        "For each requested explanation section, produce a JSON value that is both human-readable and machine-parsable. "
        "Return strictly valid JSON with top-level keys matching the requested section IDs."
    )
    user_prompt = (
        f"Solver Response:\n{json.dumps(request.solver_response)}\n"
        f"Requested Sections: {request.sections}\n"
        f"Visualization Type: {request.visualization}\n"
        "Provide a JSON object mapping each section ID to its explanation content."
    )
    try:
        resp = openai.ChatCompletion.create(
            model=request.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=request.temperature
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")
    text = resp.choices[0].message.content
    try:
        data = json.loads(text)
    except Exception:
        raise HTTPException(status_code=502, detail=f"Failed to parse LLM response as JSON: {text}")
    explanations = []
    for sec in request.sections:
        explanations.append(SectionExplanation(
            id=sec,
            content=data.get(sec),
            view_type=request.visualization
        ))
    return ExplainResponse(explanations=explanations)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
@app.get("/flows", response_model=FlowsResponse)
def list_flows():
    """List all available solver flows and their endpoints."""
    items = []
    for pt in solver_service.solvers.keys():
        endpoint = f"/solve/{pt.replace('_', '-') }"
        desc = FLOW_DESCRIPTIONS.get(pt)
        schema = FLOW_SCHEMAS.get(pt)
        items.append(FlowItem(id=pt, endpoint=endpoint, description=desc, mcpModelSchema=schema))
    return FlowsResponse(flows=items)