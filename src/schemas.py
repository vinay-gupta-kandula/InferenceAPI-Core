from pydantic import BaseModel, Field

class GenerationRequest(BaseModel):
    """
    This defines the exact rules for incoming user requests.
    """
    prompt: str = Field(
        ..., 
        min_length=10, 
        max_length=500, 
        description="The input text for the model to continue."
    )
    max_new_tokens: int = Field(
        default=50, 
        ge=10, 
        le=256, 
        description="The maximum number of new tokens (words/syllables) to generate."
    )

class GenerationResponse(BaseModel):
    """
    This defines the exact structure of the response we send back to the user.
    """
    generated_text: str