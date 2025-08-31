from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

Priority = Literal["high", "medium", "low"]

class Schedule(BaseModel):
    title: str = Field(default="일정")
    description: str = Field(default="")
    date: str  # YYYY-MM-DD
    time: Optional[str] = None  # HH:MM
    priority: Priority = "medium"
    category: str = "personal"
    recurring: bool = False
    recurrence: Optional[str] = None

    @field_validator("date")
    @classmethod
    def _date_fmt(cls, v:str)->str:
        import datetime
        datetime.datetime.strptime(v, "%Y-%m-%d")
        return v

    @field_validator("time")
    @classmethod
    def _time_fmt(cls, v:Optional[str])->Optional[str]:
        import datetime
        if v is None:
            return v
        datetime.datetime.strptime(v, "%H:%M")
        return v
