# InferenceAPI-Core: Scalable LLM Service

A high-performance RESTful API built with FastAPI for serving a pre-trained Large Language Model (LLM). This project bridges model research and MLOps by addressing asynchronous event management, memory footprints, and multi-stage containerization.

## 🚀 Local Setup Instructions

To run this project locally without Docker, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd InferenceAPI-Core

```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate
# On Linux/Mac:
source venv/bin/activate

```


3. **Install pinned dependencies:**
```bash
pip install -r requirements.txt

```


4. **Set up your environment variables:**
Rename `.env.example` to `.env` or create a new `.env` file at the root:
```text
MODEL_NAME=distilgpt2
PORT=8000

```


5. **Start the ASGI server:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000

```



## 🐳 Docker Execution Guide

This application is packaged using a multi-stage Docker build to ensure a minimal and secure production footprint.

To deploy the entire stack with a single command, ensure Docker Desktop is running and execute:

```bash
docker-compose up --build

```

The API will be instantly accessible at `http://localhost:8000/docs`.

## ⚡ API Usage Examples

Once the server is running (either locally or via Docker), you can interact with the API using the following `curl` commands.

**1. Health Check (GET /health)**
Used by orchestrators like Kubernetes to verify container health.

```bash
curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'

```

**2. Generate Text (POST /v1/generate)**

```bash
curl -X 'POST' \
  'http://localhost:8000/v1/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "The future of artificial intelligence is",
  "max_new_tokens": 50
}'

```

## 🏗️ Architectural Decision Records (ADR)

**1. Asynchronous Concurrency & Thread Pooling**
Model inference is a highly CPU-bound mathematical operation. If executed directly inside FastAPI's `async def` routing function, it would completely block the ASGI event loop, causing concurrent health checks to fail and hanging the server. To solve this, the inference pipeline is explicitly offloaded to a background thread using `asyncio.get_running_loop().run_in_executor()`. This guarantees the main thread remains responsive to incoming network traffic.

**2. The Singleton Cache Pattern**
Loading LLM weights from disk to RAM is an I/O heavy operation that takes several seconds. Dynamically loading the model per request is a severe anti-pattern. This architecture utilizes a Singleton caching mechanism (`src/model_loader.py`) triggered by FastAPI's lifespan context manager. The Hugging Face pipeline is instantiated exactly once during server startup and securely held in memory, reducing subsequent request latency to pure inference time.

**3. V2 Scalability & Bottlenecks**
While the current architecture successfully isolates the event loop, the default thread pool processes requests individually. In a high-traffic production environment (V2), the primary bottleneck would be GPU/CPU underutilization due to a lack of **dynamic request batching**. A future iteration would implement a continuous batching queue (e.g., using Ray Serve or vLLM) to group concurrent prompts into a single matrix multiplication pass, drastically increasing token throughput. Additionally, model weights are currently downloaded at container runtime; a true production Dockerfile would bake the weights directly into the image volume to prevent cold-start download delays.

