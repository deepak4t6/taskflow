from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Project Schemas ---
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    owner_id: int

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="Priority must be low, medium, or high")
    status: Literal["todo", "in_progress", "done"] = Field(default="todo", description="Status must be todo, in_progress, or done")
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_blank(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Title cannot be empty or blank whitespace")
        return str(v).strip()

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    due_date: Optional[str] = None
    project_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not str(v).strip():
                raise ValueError("Title cannot be empty or blank whitespace")
            return str(v).strip()
        return v

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"]
    status: Literal["todo", "in_progress", "done"]
    due_date: Optional[str] = None
    project_id: int

    model_config = ConfigDict(from_attributes=True)
