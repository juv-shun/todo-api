from typing import Optional
from pydantic import BaseModel, Field


class TodoTaskIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: Optional[str] = Field(None, max_length=1000)


class TodoTaskOut(TodoTaskIn):
    id: int = Field(..., ge=1)
