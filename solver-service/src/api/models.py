from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Variable(BaseModel):
    name: str
    type: str  # "continuous", "integer", "binary"
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class Constraint(BaseModel):
    name: str
    expression: str
    # Support both traditional LP operator/rhs and bound-based syntax
    operator: Optional[str] = None
    rhs: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class Objective(BaseModel):
    type: str  # "minimize" or "maximize"
    expression: str

class ModelBuildRequest(BaseModel):
    name: str
    description: Optional[str] = None
    variables: List[Variable]
    constraints: List[Constraint]
    objective: Objective
    parameters: Optional[Dict[str, Any]] = None

class ModelRunRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    solver_config: Optional[Dict[str, Any]] = None 
    
# Explainability endpoint models
class ExplainRequest(BaseModel):
    solver_response: Dict[str, Any]
    sections: List[str]
    visualization: str
    llm_model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7

class SectionExplanation(BaseModel):
    id: str
    content: Any
    view_type: str

class ExplainResponse(BaseModel):
    explanations: List[SectionExplanation]
    
class FlowItem(BaseModel):
    id: str
    endpoint: str
    description: Optional[str] = None
    mcpModelSchema: Optional[Dict[str, Any]] = None

class FlowsResponse(BaseModel):
    flows: List[FlowItem]