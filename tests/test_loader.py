import pytest
from unittest.mock import patch
import src.model_loader as ml

# We use @patch to "fake" the Hugging Face pipeline so we don't 
# actually download the 300MB model every time we run our tests!
@patch("src.model_loader.pipeline")
def test_singleton_loader(mock_pipeline_function):
    # Ensure our cache is empty before the test starts
    ml._model_pipeline = None
    
    # Simulate the server starting up and calling the loader TWICE
    ml.load_model_pipeline()
    ml.load_model_pipeline()
    
    # ASSERTION: Even though we called it twice, the expensive 
    # Hugging Face pipeline function should have only run exactly ONCE.
    mock_pipeline_function.assert_called_once()
    
    # Verify our getter function correctly returns the cached object
    assert ml.get_model_pipeline() is not None