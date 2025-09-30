from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TaskEvent(BaseModel):
    event: str  # task_created, task_updated, task_completed, task_deleted
    task_id: Optional[int] = None  # Optional for project events
    project_id: Optional[int] = None
    user_id: str  # Comes as string from Kafka
    username: str
    title: Optional[str] = None
    name: Optional[str] = None  # For project names
    status: Optional[str] = None
    timestamp: datetime
    
    # Accept any additional fields
    class Config:
        extra = "allow"


class ProjectEvent(BaseModel):
    event: str  # project_created, project_updated, project_deleted
    project_id: Optional[int] = None
    user_id: str  # Comes as string from Kafka
    username: str
    name: Optional[str] = None  # Project name
    timestamp: datetime
    
    # Accept any additional fields
    class Config:
        extra = "allow"


class UserMetrics(BaseModel):
    user_id: int
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
    user_id: int
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


class DashboardResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    active_projects: int
    completion_rate: float
    recent_activity: List[Dict[str, Any]]


class ProductivityResponse(BaseModel):
    daily_completions: Dict[str, int]
    weekly_summary: Dict[str, Any]
    productivity_score: float
    recommendations: List[str]


class ProjectAnalyticsResponse(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    avg_completion_time_hours: Optional[float]
    task_distribution: Dict[str, int]
    timeline: List[Dict[str, Any]]


class TaskSummaryResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    tasks_by_status: Dict[str, int]
    recent_completions: List[Dict[str, Any]]