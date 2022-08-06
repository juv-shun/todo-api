from typing import Optional

from pydantic import BaseModel, Field


class TodoTaskIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="タスクのタイトル")
    content: Optional[str] = Field(None, max_length=1000, description="タスクの内容")


class TodoTaskOut(TodoTaskIn):
    id: int = Field(..., ge=1, description="タスクID")
