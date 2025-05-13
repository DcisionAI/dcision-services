from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gpt4all import GPT4All
import os

def download_model_from_gcs(bucket_name, model_filename):
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(model_filename)
    if not os.path.exists(model_filename):
        print(f"Downloading {model_filename} from GCS bucket {bucket_name}...")
        try:
            blob.download_to_filename(model_filename)
            print("Download complete.")
        except Exception as e:
            print("Failed to download model from GCS:", e)
            raise
    else:
        print(f"Model file {model_filename} already exists locally.")

# Set these via environment variables or hardcode for now
GCS_BUCKET = os.environ.get("GCS_BUCKET", "dcisionai-models")  # unused when model is baked
# Default to the baked GGUF model filename if not overridden
MODEL_FILENAME = os.environ.get("GPT4ALL_MODEL_PATH", "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf")

app = FastAPI()
gpt4all = None
model_ready = False

async def init_model():
    """
    Download the model from GCS and initialize the GPT4All instance.
    Runs in a background task so that the server can bind quickly.
    """
    global gpt4all, model_ready
    try:
        download_model_from_gcs(GCS_BUCKET, MODEL_FILENAME)
        print("Model file exists after download:", os.path.exists(MODEL_FILENAME))
        print("Current directory contents:", os.listdir("."))
        # Initialize GPT4All using the local file; disable remote downloads
        gpt4all = GPT4All(
            MODEL_FILENAME,
            model_path=os.getcwd(),
            allow_download=False
        )
        model_ready = True
        print("Model loaded and ready to serve.")
    except Exception as e:
        print("Error initializing model:", e)
        import traceback
        traceback.print_exc()
        # model_ready remains False; requests will return 503

@app.on_event("startup")
async def startup_event():
    global gpt4all, model_ready
    print("Starting model initialization...")
    try:
        await init_model()
    except Exception as e:
        print("Exception during model initialization:", e)
    print("Startup event completed.")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    global gpt4all, model_ready
    # If the model is still loading or failed to load, reject requests
    if not model_ready or gpt4all is None:
        # Service is up but model still loading
        return JSONResponse(
            status_code=503,
            content={"error": "Model is initializing, please retry in a moment."}
        )
    body = await request.json()
    messages = body.get("messages", [])
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"System: {msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"Assistant: {msg['content']}\n"
    prompt += "Assistant:"

    # Generate response
    response = gpt4all.generate(prompt, max_tokens=256, temp=0.7)
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.strip()
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response.split()),
            "total_tokens": len(prompt.split()) + len(response.split())
        }
    }


@app.get("/health")
async def health():
    """Service readiness check. Returns 'ready' when the model is loaded."""
    if model_ready and gpt4all is not None:
        return {"status": "ready"}
    return {"status": "initializing"}