from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

class PersonaResponse(BaseModel):
    persona: str
    content: str
    tips: Optional[List[str]] = None
