from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class TaskEvent(BaseModel):
    event: str  # internal normalized: task_created, task_updated, etc.
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    user_id: str
    username: str
    title: Optional[str] = None
    status: Optional[str] = None
    timestamp: datetime

    class Config:
        extra = "allow"


class UserMetrics(BaseModel):
    user_id: str
    username: str
    total_tasks: int = 0
    completed_tasks: int = 0
    active_projects: int = 0
    completion_rate: float = 0.0
    avg_completion_time_hours: Optional[float] = None
    last_activity: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectMetrics(BaseModel):
    project_id: int
    user_id: str
    username: str
    project_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    completion_rate: float = 0.0
    avg_completion_time_hours: Optional[float] = None
    created_at_project: datetime
    last_activity: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))