# Solver Service

A FastAPI-based service that provides intent recognition for optimization problems in FleetOps and Workforce Management domains.

## Features

- Intent recognition for FleetOps problems:
  - Vehicle Assignment
  - Fleet Mix Optimization
  - Maintenance Scheduling
  - Fuel Management

- Intent recognition for Workforce Management problems:
  - Employee Scheduling
  - Skill Matching
  - Shift Optimization
  - Workload Balancing

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service

Start the service using Uvicorn:

```bash
uvicorn src.service:app --reload
```

The service will be available at `http://localhost:8000`

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /identify-problem

Identify the problem type and extract context, constraints, and objectives from the input text.

Request body:
```json
{
    "domain": "fleetops",  // or "workforce"
    "input_text": "I need to assign vehicles to delivery routes while minimizing fuel costs and respecting time windows"
}
```

Response:
```json
{
    "problem_type": "vehicle_assignment",
    "context": {
        "has_time_windows": true,
        "has_capacity": false,
        "has_skills": false
    },
    "constraints": [
        "respecting time windows"
    ],
    "objectives": [
        "minimizing fuel costs"
    ]
}
```

### GET /health

Health check endpoint that returns the service status.

## Development

The service is structured as follows:

```
solver-service/
├── src/
│   ├── domains/
│   │   ├── base/
│   │   │   └── agent.py
│   │   ├── fleetops/
│   │   │   └── agents/
│   │   │       └── intent_agent.py
│   │   ├── workforce/
│   │   │   └── agents/
│   │   │       └── intent_agent.py
│   │   └── factory.py
│   └── service.py
├── requirements.txt
└── README.md
```

- `base/agent.py`: Contains the base intent agent class with common functionality
- `fleetops/agents/intent_agent.py`: FleetOps-specific intent recognition
- `workforce/agents/intent_agent.py`: Workforce-specific intent recognition
- `factory.py`: Factory class for creating intent agents
- `service.py`: FastAPI application with endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 