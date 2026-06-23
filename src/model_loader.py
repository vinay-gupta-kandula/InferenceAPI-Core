import os
from transformers import pipeline

# This global variable acts as our cache
_model_pipeline = None

def load_model_pipeline():
    """
    Loads the Hugging Face model into system memory exactly once.
    """
    global _model_pipeline
    
    # Check if the model is already loaded
    if _model_pipeline is None:
        # Securely read the model name from environment variables
        model_name = os.getenv("MODEL_NAME", "distilgpt2")
        print(f"Loading model '{model_name}' into memory. This may take a few seconds...")
        
        # Initialize the text-generation pipeline
        _model_pipeline = pipeline("text-generation", model=model_name)
        print("Model loaded successfully!")

def get_model_pipeline():
    """
    Safely retrieves the cached model for the API to use.
    """
    if _model_pipeline is None:
        raise RuntimeError("Model pipeline is not initialized. Call load_model_pipeline() at startup.")
    
    return _model_pipeline