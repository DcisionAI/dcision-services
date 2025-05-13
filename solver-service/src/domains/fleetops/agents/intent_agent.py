from typing import Dict, Any, List
from pydantic import BaseModel
from enum import Enum
from ...base.agent import BaseIntentAgent, BaseIntentContext

class FleetOpsProblemType(str, Enum):
    VEHICLE_ASSIGNMENT = "vehicle_assignment"
    FLEET_MIX = "fleet_mix"
    MAINTENANCE = "maintenance"
    FUEL = "fuel"

class IntentContext(BaseIntentContext[FleetOpsProblemType]):
    pass

class FleetOpsIntentAgent(BaseIntentAgent[FleetOpsProblemType]):
    def __init__(self):
        problem_keywords = {
            FleetOpsProblemType.VEHICLE_ASSIGNMENT: [
                "assign", "vehicle", "route", "delivery", "dispatch"
            ],
            FleetOpsProblemType.FLEET_MIX: [
                "fleet", "mix", "composition", "vehicle types", "capacity"
            ],
            FleetOpsProblemType.MAINTENANCE: [
                "maintenance", "service", "repair", "inspection", "schedule"
            ],
            FleetOpsProblemType.FUEL: [
                "fuel", "refuel", "consumption", "efficiency", "cost"
            ]
        }
        super().__init__(problem_keywords)

    def _extract_context(self, input_text: str, problem_type: FleetOpsProblemType) -> Dict[str, Any]:
        """Extract relevant context based on problem type."""
        context = {}
        
        if problem_type == FleetOpsProblemType.VEHICLE_ASSIGNMENT:
            context["has_time_windows"] = "time window" in input_text
            context["has_capacity"] = "capacity" in input_text
            context["has_skills"] = "skill" in input_text or "requirement" in input_text
            
        elif problem_type == FleetOpsProblemType.FLEET_MIX:
            context["has_budget"] = "budget" in input_text or "cost" in input_text
            context["has_demand"] = "demand" in input_text or "forecast" in input_text
            
        elif problem_type == FleetOpsProblemType.MAINTENANCE:
            context["has_facilities"] = "facility" in input_text or "location" in input_text
            context["has_parts"] = "part" in input_text or "component" in input_text
            
        elif problem_type == FleetOpsProblemType.FUEL:
            context["has_stations"] = "station" in input_text or "depot" in input_text
            context["has_prices"] = "price" in input_text or "cost" in input_text
            
        return context

    def _extract_constraints(self, input_text: str) -> List[str]:
        """Extract constraints from input text."""
        constraint_keywords = [
            "must", "should", "require", "constraint", "limit",
            "maximum", "minimum", "at least", "at most", "no more than"
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
            "best", "efficient", "optimal", "improve"
        ]
        
        objectives = []
        words = input_text.split()
        
        for i, word in enumerate(words):
            if word in objective_keywords:
                # Get the objective phrase
                objective = " ".join(words[i:i+5])  # Get next 5 words
                objectives.append(objective)
                
        return objectives 