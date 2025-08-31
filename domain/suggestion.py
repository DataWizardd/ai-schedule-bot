from pydantic import BaseModel
from typing import Optional, Literal

Priority = Literal["high", "medium", "low"]

class Suggestion(BaseModel):
    title: str
    description: str
    suggested_date: str
    suggested_time: Optional[str] = None
    priority: Priority = "medium"
    category: str = "personal"
