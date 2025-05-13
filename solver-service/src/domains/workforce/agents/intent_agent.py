from typing import Dict, Any, List
from pydantic import BaseModel
from enum import Enum
from ...base.agent import BaseIntentAgent, BaseIntentContext

class WorkforceProblemType(str, Enum):
    SCHEDULING = "scheduling"
    SKILL_MATCHING = "skill_matching"
    SHIFT_OPTIMIZATION = "shift_optimization"
    WORKLOAD_BALANCING = "workload_balancing"

class IntentContext(BaseIntentContext[WorkforceProblemType]):
    pass

class WorkforceIntentAgent(BaseIntentAgent[WorkforceProblemType]):
    def __init__(self):
        problem_keywords = {
            WorkforceProblemType.SCHEDULING: [
                "schedule", "shift", "roster", "time", "availability"
            ],
            WorkforceProblemType.SKILL_MATCHING: [
                "skill", "qualification", "certification", "expertise", "match"
            ],
            WorkforceProblemType.SHIFT_OPTIMIZATION: [
                "optimize", "shift", "pattern", "rotation", "coverage"
            ],
            WorkforceProblemType.WORKLOAD_BALANCING: [
                "workload", "balance", "fair", "distribution", "equitable"
            ]
        }
        super().__init__(problem_keywords)

    def _extract_context(self, input_text: str, problem_type: WorkforceProblemType) -> Dict[str, Any]:
        """Extract relevant context based on problem type."""
        context = {}
        
        if problem_type == WorkforceProblemType.SCHEDULING:
            context["has_preferences"] = "preference" in input_text or "request" in input_text
            context["has_breaks"] = "break" in input_text or "rest" in input_text
            context["has_legal"] = "legal" in input_text or "compliance" in input_text
            
        elif problem_type == WorkforceProblemType.SKILL_MATCHING:
            context["has_certifications"] = "certification" in input_text or "license" in input_text
            context["has_experience"] = "experience" in input_text or "seniority" in input_text
            context["has_training"] = "training" in input_text or "development" in input_text
            
        elif problem_type == WorkforceProblemType.SHIFT_OPTIMIZATION:
            context["has_demand"] = "demand" in input_text or "forecast" in input_text
            context["has_costs"] = "cost" in input_text or "budget" in input_text
            context["has_coverage"] = "coverage" in input_text or "requirement" in input_text
            
        elif problem_type == WorkforceProblemType.WORKLOAD_BALANCING:
            context["has_metrics"] = "metric" in input_text or "kpi" in input_text
            context["has_fairness"] = "fair" in input_text or "equitable" in input_text
            context["has_capacity"] = "capacity" in input_text or "limit" in input_text
            
        return context

    def _extract_constraints(self, input_text: str) -> List[str]:
        """Extract constraints from input text."""
        constraint_keywords = [
            "must", "should", "require", "constraint", "limit",
            "maximum", "minimum", "at least", "at most", "no more than",
            "compliance", "regulation", "policy"
        ]
        
        constraints = []
        words = input_text.split()
        
        for i, word in enumerate(words):
            if word in constraint_keywords:
                # Get the constraint phrase
                constraint = " ".join(words[i:i+5])  # Get next 5 words
                constraints.append(constraint)
                
        return constraints

    def _extract_objectives(self, input_text: str) -> List[str]:
        """Extract objectives from input text."""
        objective_keywords = [
            "minimize", "maximize", "optimize", "reduce", "increase",
            "best", "efficient", "optimal", "improve", "balance",
            "fair", "equitable", "satisfy"
        ]
        
        objectives = []
        words = input_text.split()
        
        for i, word in enumerate(words):
            if word in objective_keywords:
                # Get the objective phrase
                objective = " ".join(words[i:i+5])  # Get next 5 words
                objectives.append(objective)
                
        return objectives 