from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

# Using 'with TestClient(app)' is crucial because it triggers our 
# FastAPI lifespan events (startup/shutdown) automatically in the test.

def test_health_check():
    """Test if the server is alive and returning 200 OK."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

# We mock the model loader so the test runs in 0.1 seconds instead of 10 seconds.
@patch("src.main.get_model_pipeline")
@patch("src.main.load_model_pipeline") 
def test_generate_success(mock_load, mock_get):
    """Test if a valid prompt returns a 200 OK and generated text."""
    # Fake the AI's output
    mock_pipeline = mock_get.return_value
    mock_pipeline.return_value = [{"generated_text": "Mocked generated text"}]
    
    with TestClient(app) as client:
        response = client.post(
            "/v1/generate", 
            json={"prompt": "This is a valid prompt.", "max_new_tokens": 20}
        )
        assert response.status_code == 200
        assert "generated_text" in response.json()

def test_generate_validation_errors():
    """Test if Pydantic successfully blocks malicious/bad requests."""
    with TestClient(app) as client:
        # 1. Test a prompt that is too short (under 10 characters)
        response_short = client.post("/v1/generate", json={"prompt": "short"})
        assert response_short.status_code == 422
        
        # 2. Test asking for too many tokens (over 256)
        response_tokens = client.post(
            "/v1/generate", 
            json={"prompt": "This is a valid prompt.", "max_new_tokens": 500}
        )
        assert response_tokens.status_code == 422