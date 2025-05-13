from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .domains.factory import IntentAgentFactory, DomainType

app = FastAPI(title="Solver Service")

class ProblemRequest(BaseModel):
    domain: str
    input_text: str

class ProblemResponse(BaseModel):
    problem_type: str
    context: Dict[str, Any]
    constraints: list[str]
    objectives: list[str]

@app.post("/identify-problem", response_model=ProblemResponse)
async def identify_problem(request: ProblemRequest):
    try:
        # Get the appropriate intent agent
        agent = IntentAgentFactory.get_agent(request.domain)
        
        # Identify the problem
        intent_context = await agent.identify_problem(request.input_text)
        
        return ProblemResponse(
            problem_type=intent_context.problem_type.value,
            context=intent_context.context,
            constraints=intent_context.constraints,
            objectives=intent_context.objectives
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 