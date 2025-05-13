from typing import Dict, Any, List, TypeVar, Generic
from pydantic import BaseModel
from enum import Enum

T = TypeVar('T', bound=Enum)

class BaseIntentContext(BaseModel, Generic[T]):
    problem_type: T
    context: Dict[str, Any]
    constraints: List[str]
    objectives: List[str]

class BaseIntentAgent(Generic[T]):
    def __init__(self, problem_keywords: Dict[T, List[str]]):
        self.problem_keywords = problem_keywords

    async def identify_problem(self, user_input: str) -> BaseIntentContext[T]:
        """Identify the problem type from user input."""
        input_lower = user_input.lower()
        
        # Find the problem type with the most matching keywords
        problem_scores = {
            problem_type: sum(1 for keyword in keywords if keyword in input_lower)
            for problem_type, keywords in self.problem_keywords.items()
        }
        
        if not any(problem_scores.values()):
            raise ValueError("Could not identify a valid problem type")
            
        problem_type = max(problem_scores.items(), key=lambda x: x[1])[0]
        
        # Extract context, constraints, and objectives
        context = self._extract_context(input_lower, problem_type)
        constraints = self._extract_constraints(input_lower)
        objectives = self._extract_objectives(input_lower)
        
        return BaseIntentContext(
            problem_type=problem_type,
            context=context,
            constraints=constraints,
            objectives=objectives
        )

    def _extract_context(self, input_text: str, problem_type: T) -> Dict[str, Any]:
        """Extract relevant context based on problem type."""
        raise NotImplementedError("Subclasses must implement _extract_context")

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