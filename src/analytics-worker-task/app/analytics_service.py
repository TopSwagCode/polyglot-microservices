from datetime import datetime, timezone
import structlog
from app.database import get_database
from app.models import TaskEvent, UserMetrics, ProjectMetrics

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self):
        self._db = None

    def _get_db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    async def update_task_metrics(self, task_event: TaskEvent):
        try:
            await self._update_user_metrics(task_event)
            await self._update_project_metrics_from_task(task_event)
        except Exception as e:
            logger.error("Error updating task metrics", error=str(e), exc_info=True)

    async def _update_user_metrics(self, task_event: TaskEvent):
        db = self._get_db()
        user_metrics = await db.user_metrics.find_one({"user_id": task_event.user_id})
        if user_metrics is None:
            user_metrics = UserMetrics(user_id=task_event.user_id, username=task_event.username).model_dump()
        # Ensure keys
        for k, v in {"total_tasks": 0, "completed_tasks": 0, "completion_rate": 0.0}.items():
            user_metrics.setdefault(k, v)
        if task_event.event == "task_created":
            user_metrics["total_tasks"] += 1
        elif task_event.event == "task_updated" and task_event.status == "completed":
            user_metrics["completed_tasks"] += 1
        elif task_event.event == "task_deleted":
            user_metrics["total_tasks"] = max(0, user_metrics["total_tasks"] - 1)
            if task_event.status == "completed":
                user_metrics["completed_tasks"] = max(0, user_metrics["completed_tasks"] - 1)
        if user_metrics["total_tasks"] > 0:
            user_metrics["completion_rate"] = user_metrics["completed_tasks"] / user_metrics["total_tasks"]
        else:
            user_metrics["completion_rate"] = 0.0
        user_metrics["last_activity"] = task_event.timestamp
        user_metrics["updated_at"] = datetime.now(timezone.utc)
        await db.user_metrics.replace_one({"user_id": task_event.user_id}, user_metrics, upsert=True)

    async def _update_project_metrics_from_task(self, task_event: TaskEvent):
        if not task_event.project_id:
            return
        db = self._get_db()
        project_metrics = await db.project_metrics.find_one({
            "project_id": task_event.project_id,
            "user_id": task_event.user_id
        })
        if project_metrics is None:
            project_metrics = ProjectMetrics(
                project_id=task_event.project_id,
                user_id=task_event.user_id,
                username=task_event.username,
                project_name=f"Project {task_event.project_id}",
                created_at_project=task_event.timestamp
            ).model_dump()
        for k, v in {"total_tasks": 0, "completed_tasks": 0, "completion_rate": 0.0}.items():
            project_metrics.setdefault(k, v)
        if task_event.event == "task_created":
            project_metrics["total_tasks"] += 1
        elif task_event.event == "task_updated" and task_event.status == "completed":
            project_metrics["completed_tasks"] += 1
        elif task_event.event == "task_deleted":
            project_metrics["total_tasks"] = max(0, project_metrics["total_tasks"] - 1)
            if task_event.status == "completed":
                project_metrics["completed_tasks"] = max(0, project_metrics["completed_tasks"] - 1)
        if project_metrics["total_tasks"] > 0:
            project_metrics["completion_rate"] = project_metrics["completed_tasks"] / project_metrics["total_tasks"]
        else:
            project_metrics["completion_rate"] = 0.0
        project_metrics["last_activity"] = task_event.timestamp
        project_metrics["updated_at"] = datetime.now(timezone.utc)
        await db.project_metrics.replace_one({"project_id": task_event.project_id, "user_id": task_event.user_id}, project_metrics, upsert=True)