from typing import Dict, Any
import uuid
from datetime import datetime, timedelta

class ModelStore:
    def __init__(self):
        self._models: Dict[str, Dict[str, Any]] = {}
        self._model_expiry = timedelta(hours=24)  # Models expire after 24 hours

    def store_model(self, model_data: Dict[str, Any]) -> str:
        model_id = str(uuid.uuid4())
        self._models[model_id] = {
            "data": model_data,
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }
        return model_id

    def get_model(self, model_id: str) -> Dict[str, Any]:
        if model_id not in self._models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self._models[model_id]
        model["last_accessed"] = datetime.now()
        return model["data"]

    def delete_model(self, model_id: str) -> None:
        if model_id in self._models:
            del self._models[model_id]

    def cleanup_expired_models(self) -> None:
        current_time = datetime.now()
        expired_models = [
            model_id for model_id, model in self._models.items()
            if current_time - model["created_at"] > self._model_expiry
        ]
        for model_id in expired_models:
            self.delete_model(model_id)

model_store = ModelStore() 