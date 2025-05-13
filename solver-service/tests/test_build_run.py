import requests
import json
from typing import Dict, Any

# Service URL
BASE_URL = "https://solver-service-219323644585.us-central1.run.app"

def test_build_and_run():
    # Example: Simple Production Planning Problem
    # Maximize profit: 3x + 2y
    # Subject to:
    #   x + y <= 4
    #   2x + y <= 5
    #   x, y >= 0
    
    # Step 1: Build the model
    build_request = {
        "name": "Production Planning",
        "description": "Simple production planning problem with two products",
        "variables": [
            {"name": "x", "type": "continuous", "lower_bound": 0},
            {"name": "y", "type": "continuous", "lower_bound": 0}
        ],
        "constraints": [
            {"name": "c1", "expression": "x + y <= 4"},
            {"name": "c2", "expression": "2x + y <= 5"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "3x + 2y"
        },
        "parameters": {
            "time_limit": 60,
            "tolerance": 0.0001
        }
    }
    
    print("\nBuilding model...")
    build_response = requests.post(
        f"{BASE_URL}/build",
        json=build_request
    )
    
    if build_response.status_code != 200:
        print(f"Error building model: {build_response.text}")
        return
    
    model_id = build_response.json()["model_id"]
    print(f"Model built successfully. Model ID: {model_id}")
    
    # Step 2: Run the model
    run_request = {
        "parameters": {
            "time_limit": 30
        },
        "solver_config": {
            "presolve": "on",
            "scaling": "on"
        }
    }
    
    print("\nRunning model...")
    run_response = requests.post(
        f"{BASE_URL}/run/{model_id}",
        json=run_request
    )
    
    if run_response.status_code != 200:
        print(f"Error running model: {run_response.text}")
        return
    
    solution = run_response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))

if __name__ == "__main__":
    test_build_and_run() 