from fastapi import FastAPI
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

app = FastAPI()

# Test the exact models from our models.py to isolate the issue
class TaskEvent(BaseModel):
    event_type: str  # created, updated, completed, deleted
    task_id: int
    project_id: int
    user_id: int
    username: str
    task_data: Dict[str, Any]
    timestamp: datetime

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

@app.get("/")
async def root():
    return {"message": "Testing our exact models"}

@app.post("/task-event")
async def test_task_event(data: TaskEvent):
    return {"received": data}

@app.post("/user-metrics")
async def test_user_metrics(data: UserMetrics):
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)