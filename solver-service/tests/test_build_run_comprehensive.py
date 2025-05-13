import requests
import json
from typing import Dict, Any
import time

# Service URL
BASE_URL = "https://solver-service-219323644585.us-central1.run.app"

def test_linear_programming():
    """Test a simple linear programming problem."""
    print("\nTesting Linear Programming...")
    
    build_request = {
        "name": "LP Test",
        "description": "Simple linear programming problem",
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
        }
    }
    
    run_test_case(build_request)

def test_mixed_integer_programming():
    """Test a mixed integer programming problem."""
    print("\nTesting Mixed Integer Programming...")
    
    build_request = {
        "name": "MIP Test",
        "description": "Simple mixed integer programming problem",
        "variables": [
            {"name": "x", "type": "integer", "lower_bound": 0},
            {"name": "y", "type": "binary"}
        ],
        "constraints": [
            {"name": "c1", "expression": "x + y <= 4"},
            {"name": "c2", "expression": "2x + y <= 5"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "3x + 2y"
        }
    }
    
    run_test_case(build_request)

def test_error_cases():
    """Test various error cases."""
    print("\nTesting Error Cases...")
    
    # Test invalid variable type
    print("\nTesting invalid variable type...")
    build_request = {
        "name": "Invalid Variable Test",
        "variables": [
            {"name": "x", "type": "invalid", "lower_bound": 0}
        ],
        "constraints": [],
        "objective": {
            "type": "maximize",
            "expression": "x"
        }
    }
    
    response = requests.post(f"{BASE_URL}/build", json=build_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test missing required fields
    print("\nTesting missing required fields...")
    build_request = {
        "name": "Missing Fields Test",
        "variables": [],
        "constraints": [],
        "objective": {}
    }
    
    response = requests.post(f"{BASE_URL}/build", json=build_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test invalid model ID
    print("\nTesting invalid model ID...")
    run_request = {
        "parameters": {"time_limit": 30}
    }
    
    response = requests.post(f"{BASE_URL}/run/invalid_id", json=run_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def run_test_case(build_request: Dict[str, Any]):
    """Helper function to run a test case."""
    # Build the model
    print("Building model...")
    build_response = requests.post(f"{BASE_URL}/build", json=build_request)
    
    if build_response.status_code != 200:
        print(f"Error building model: {build_response.text}")
        return
    
    model_id = build_response.json()["model_id"]
    print(f"Model built successfully. Model ID: {model_id}")
    
    # Run the model
    print("Running model...")
    run_request = {
        "parameters": {"time_limit": 30},
        "solver_config": {"presolve": "on"}
    }
    
    run_response = requests.post(f"{BASE_URL}/run/{model_id}", json=run_request)
    
    if run_response.status_code != 200:
        print(f"Error running model: {run_response.text}")
        return
    
    solution = run_response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))

def main():
    """Run all tests."""
    print("Starting comprehensive tests...")
    
    # Wait for deployment to complete
    print("Waiting for deployment to complete...")
    time.sleep(60)  # Wait 1 minute for deployment
    
    # Run tests
    test_linear_programming()
    test_mixed_integer_programming()
    test_error_cases()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 