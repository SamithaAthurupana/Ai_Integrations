from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message:str

class PersonaResponse(BaseModel):
    persona:str
    content:str
    tips:List[str]
