import requests
import json
from typing import Dict, Any
import time

# Service URL - Update this to your deployed service URL
BASE_URL = "http://localhost:8081"  # For local testing
# BASE_URL = "https://solver-service-219323644585.us-central1.run.app"  # For deployed service

def test_linear_programming():
    """Test a simple linear programming problem using the new /solve endpoint."""
    print("\nTesting Linear Programming with /solve endpoint...")
    
    solve_request = {
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
    
    print("Solving model...")
    response = requests.post(f"{BASE_URL}/solve", json=solve_request)
    
    if response.status_code != 200:
        print(f"Error solving model: {response.text}")
        return
    
    solution = response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))
    
    # Verify solution
    assert solution["status"] == "optimal", f"Expected optimal status, got {solution['status']}"
    assert abs(solution["objective_value"] - 11.0) < 0.001, f"Expected objective value ~11.0, got {solution['objective_value']}"
    assert abs(solution["solution"]["x"] - 1.0) < 0.001, f"Expected x = 1.0, got {solution['solution']['x']}"
    assert abs(solution["solution"]["y"] - 4.0) < 0.001, f"Expected y = 4.0, got {solution['solution']['y']}"

def test_expression_parsing():
    """Test the improved expression parsing with coefficients."""
    print("\nTesting Expression Parsing...")
    
    solve_request = {
        "variables": [
            {"name": "x", "type": "continuous", "lower_bound": 0}
        ],
        "constraints": [
            {"name": "c1", "expression": "x <= 5"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "2x"
        }
    }
    
    print("Solving model...")
    response = requests.post(f"{BASE_URL}/solve", json=solve_request)
    
    if response.status_code != 200:
        print(f"Error solving model: {response.text}")
        return
    
    solution = response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))
    
    # Verify solution
    assert solution["status"] == "optimal", f"Expected optimal status, got {solution['status']}"
    assert abs(solution["objective_value"] - 10.0) < 0.001, f"Expected objective value 10.0, got {solution['objective_value']}"
    assert abs(solution["solution"]["x"] - 5.0) < 0.001, f"Expected x = 5.0, got {solution['solution']['x']}"

def test_infeasible_problem():
    """Test handling of an infeasible problem."""
    print("\nTesting Infeasible Problem...")
    
    solve_request = {
        "variables": [
            {"name": "x", "type": "continuous", "lower_bound": 0}
        ],
        "constraints": [
            {"name": "c1", "expression": "x <= 5"},
            {"name": "c2", "expression": "x >= 10"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "x"
        }
    }
    
    print("Solving model...")
    response = requests.post(f"{BASE_URL}/solve", json=solve_request)
    
    if response.status_code != 200:
        print(f"Error solving model: {response.text}")
        return
    
    solution = response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))
    
    # Verify solution
    assert solution["status"] == "infeasible", f"Expected infeasible status, got {solution['status']}"

def test_unbounded_problem():
    """Test handling of an unbounded problem."""
    print("\nTesting Unbounded Problem...")
    
    solve_request = {
        "variables": [
            {"name": "x", "type": "continuous", "lower_bound": 0}
        ],
        "constraints": [],  # No constraints to make it unbounded
        "objective": {
            "type": "maximize",
            "expression": "x"
        }
    }
    
    print("Solving model...")
    response = requests.post(f"{BASE_URL}/solve", json=solve_request)
    
    if response.status_code != 200:
        print(f"Error solving model: {response.text}")
        return
    
    solution = response.json()
    print("\nSolution:")
    print(json.dumps(solution, indent=2))
    
    # Verify solution
    assert solution["status"] == "unbounded", f"Expected unbounded status, got {solution['status']}"

if __name__ == "__main__":
    print("Starting solver service tests...")
    
    # Run tests
    test_linear_programming()
    test_expression_parsing()
    test_infeasible_problem()
    test_unbounded_problem()
    
    print("\nAll tests completed!") 