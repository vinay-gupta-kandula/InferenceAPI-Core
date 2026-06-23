import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# Import our custom files
from src.schemas import GenerationRequest, GenerationResponse
from src.model_loader import load_model_pipeline, get_model_pipeline

# --- 1. Lifespan Manager (Startup Phase) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up: Wiping off the dust and loading the AI model into memory...")
    # This ensures the model is loaded BEFORE the server accepts web traffic
    load_model_pipeline()
    yield
    print("🛑 Shutting down server...")

# --- 2. Application Initialization ---
app = FastAPI(
    title="InferenceAPI-Core",
    description="Scalable Inference API using background threads.",
    version="1.0.0",
    lifespan=lifespan
)

# --- 3. Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Returns 200 OK so Docker/Kubernetes knows the server is alive."""
    return {"status": "healthy"}

# --- 4. The Main Inference Endpoint ---
@app.post("/v1/generate", response_model=GenerationResponse)
async def generate_text(request: GenerationRequest):
    """Takes user prompt, offloads calculation to a thread, returns text."""
    try:
        # Get the current asynchronous event loop
        loop = asyncio.get_running_loop()
        
        # Grab our pre-loaded model from the Singleton cache
        pipeline = get_model_pipeline()
        
        # OFF-LOAD TO BACKGROUND THREAD:
        # We tell the loop to run the heavy AI calculation in a separate thread.
        # The 'await' keyword pauses this specific user's request while the main server stays awake.
        raw_output = await loop.run_in_executor(
            None, # Use default thread pool
            lambda: pipeline(request.prompt, max_new_tokens=request.max_new_tokens)
        )
        
        # Hugging Face returns a list with a dictionary. We extract just the text.
        generated_string = raw_output[0]["generated_text"]
        
        return GenerationResponse(generated_text=generated_string)
        
    except Exception as e:
        # Log the raw error internally for debugging
        print(f"Internal Server Error during inference: {e}")
        # Return a safe, generic error to the user without leaking stack traces
        raise HTTPException(status_code=500, detail="Text generation failed")