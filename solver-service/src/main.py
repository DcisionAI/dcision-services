import os
import uvicorn
from src.api.routes import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("src.api.routes:app", host="0.0.0.0", port=port, reload=True) 