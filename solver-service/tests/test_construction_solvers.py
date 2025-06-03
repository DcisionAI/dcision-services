import json
import pytest
from fastapi.testclient import TestClient
from src.api.routes import app
import openai

client = TestClient(app)

def test_crew_allocation_success():
    payload = {
        "crews": [
            {"id": 1, "skills": ["assembly"], "availability": [[0, 8]]},
            {"id": 2, "skills": ["welding"], "availability": [[0, 8]]}
        ],
        "tasks": [
            {"id": 101, "site_id": 1, "required_skills": ["assembly"], "duration": 4},
            {"id": 102, "site_id": 1, "required_skills": ["welding"], "duration": 3}
        ],
        "shifts": [{"id": 1, "start": 0, "end": 8}],
        "union_rules": [{"max_work_hours_per_day": 8}],
        "priorities": {"1": 10}
    }
    response = client.post("/solve/crew-allocation", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assigns = data["solution"]["assignments"]
    # Should assign both tasks
    assert len(assigns) == 2

def test_subcontractor_scheduling_success():
    payload = {
        "tasks": [
            {"id": 1, "duration": 2, "predecessors": []},
            {"id": 2, "duration": 3, "predecessors": [1]}
        ],
        "time_horizon": 8
    }
    response = client.post("/solve/subcontractor-scheduling", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    sol = data["solution"]
    assert sol["makespan"] >= 5
    assert len(sol["schedule"]) == 2

def test_portfolio_balancing_success():
    payload = {
        "sites": [{"id": 1}, {"id": 2}],
        "resources": [{"id": 1, "count": 10}],
        "weights": {"1": 2.0, "2": 1.0},
        "constraints": {"min_allocations": {"1": 2, "2": 1}, "max_allocations": {"1": 8, "2": 5}}
    }
    response = client.post("/solve/portfolio-balancing", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    allocations = data["solution"]["allocations"]
    assert sum(allocations.values()) <= 10

def test_change_order_impact():
    payload = {
        "original_plan": {"tasks": [
            {"id": 1, "duration": 3, "predecessors": []},
            {"id": 2, "duration": 4, "predecessors": [1]}
        ]},
        "change_orders": [{"task_id": 2, "duration_delta": 2}]
    }
    response = client.post("/solve/change-order-impact", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["solution"]["new_makespan"] == 3 + (4 + 2)

def test_compliance_planning_success():
    payload = {
        "tasks": [{"id": 1, "duration": 2}, {"id": 2, "duration": 3}],
        "blackout_windows": [[2, 4]],
        "constraints": {"time_horizon": 8}
    }
    response = client.post("/solve/compliance-planning", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    sol = data["solution"]
    # Ensure no task overlaps blackout [2,4]
    for ev in sol["schedule"]:
        assert not (ev["start"] < 4 and ev["end"] > 2)

def test_explain_endpoint(monkeypatch):
    # Mock OpenAI response
    expected = {"feature-importance": {"x": 1}}
    class Dummy:
        def __init__(self):
            self.choices = [type('C', (), {'message': type('M', (), {'content': json.dumps(expected)})()})]
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(openai.ChatCompletion, 'create', lambda **kwargs: Dummy())
    payload = {
        "solver_response": {"dummy": 1},
        "sections": ["feature-importance"],
        "visualization": "table"
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["explanations"][0]["id"] == "feature-importance"
    assert data["explanations"][0]["content"] == expected["feature-importance"]
def test_flows_endpoint():
    response = client.get("/flows")
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'flows' in data
    # Expect at least one known flow
    ids = [f['id'] for f in data['flows']]
    assert 'crew_allocation' in ids