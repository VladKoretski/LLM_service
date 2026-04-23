from pydantic import BaseModel, Field
from typing import Optional, Dict

class TextInput(BaseModel):
    text: str = Field(..., min_length=5, max_length=2000, description="Текст для обработки")

class ProcessResponse(BaseModel):
    result: str
    source: str  # "llm", "cache", "fallback"
    metadata: Optional[Dict] = None