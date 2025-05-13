from typing import Dict, Type, Any
from .fleetops.agents.intent_agent import FleetOpsIntentAgent, FleetOpsProblemType
from .workforce.agents.intent_agent import WorkforceIntentAgent, WorkforceProblemType
from .base.agent import BaseIntentAgent

class DomainType(str):
    FLEETOPS = "fleetops"
    WORKFORCE = "workforce"

class IntentAgentFactory:
    _agents: Dict[str, BaseIntentAgent] = {}
    
    @classmethod
    def get_agent(cls, domain: str) -> BaseIntentAgent:
        """Get an intent agent for the specified domain."""
        if domain not in cls._agents:
            if domain == DomainType.FLEETOPS:
                cls._agents[domain] = FleetOpsIntentAgent()
            elif domain == DomainType.WORKFORCE:
                cls._agents[domain] = WorkforceIntentAgent()
            else:
                raise ValueError(f"Unknown domain: {domain}")
                
        return cls._agents[domain]
    
    @classmethod
    def clear_agents(cls):
        """Clear all cached agents."""
        cls._agents.clear() 