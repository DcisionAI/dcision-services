import requests
import json

# Sample VRP data from Google OR-Tools documentation
sample_data = {
    "type": "VEHICLE_ROUTING",
    "variables": {
        "locations": [
            {"id": i} for i in range(17)  # 17 locations including depot
        ],
        "vehicles": 4,
        "depot": 0,
        "distance_matrix": [
            [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
            [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
            [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
            [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
            [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
            [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
            [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
            [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
            [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
            [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
            [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
            [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
            [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
            [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
            [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
            [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
            [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0]
        ],
        # We'll set simple demands and capacities since they're not in the original example
        "demands": [0] + [1] * 16,  # Depot has 0 demand, all other locations have demand of 1
        "vehicle_capacities": [5] * 4,  # Each vehicle can handle 5 locations
        # Set generous time windows
        "time_windows": [[0, 1000]] * 17,
        "service_times": [0] * 17
    },
    "constraints": {
        "capacity_constraint": True,
        "time_window_constraint": False  # Simplified to focus on basic routing first
    },
    "objective": {
        "type": "minimize",
        "function": "total_distance"
    }
}

def test_vrp_solver():
    try:
        response = requests.post(
            "http://localhost:8000/solve",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            solution = response.json()
            print("Solution received:")
            print(json.dumps(solution, indent=2))
            
            if solution["status"] == "OPTIMAL":
                print("\nRoute Summary:")
                for route in solution["solution"]["routes"]:
                    print(f"\nVehicle {route['vehicle_id']}:")
                    print(f"Distance: {route['distance']}")
                    print("Route:", " -> ".join(str(loc['location_id']) for loc in route['route']))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_vrp_solver() 