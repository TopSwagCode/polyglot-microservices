from datetime import datetime, timezone
import structlog
from app.database import get_database
from app.models import ProjectEvent, ProjectMetrics

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self):
        self._db = None

    def _get_db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    async def update_project_metrics(self, project_event: ProjectEvent):
        try:
            await self._update_user_project_count(project_event)
            await self._update_project_metrics_from_project(project_event)
        except Exception as e:
            logger.error("Error updating project metrics", error=str(e), exc_info=True)

    async def _update_user_project_count(self, project_event: ProjectEvent):
        db = self._get_db()
        active_projects = await db.project_metrics.count_documents({"user_id": project_event.user_id})
        await db.user_metrics.update_one(
            {"user_id": project_event.user_id},
            {"$set": {"active_projects": active_projects, "last_activity": project_event.timestamp, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    async def _update_project_metrics_from_project(self, project_event: ProjectEvent):
        db = self._get_db()
        if project_event.event == "project_created":
            metrics = ProjectMetrics(
                project_id=project_event.project_id,
                user_id=project_event.user_id,
                username=project_event.username,
                project_name=project_event.name or f"Project {project_event.project_id}",
                created_at_project=project_event.timestamp,
            )
            await db.project_metrics.insert_one(metrics.model_dump())
        elif project_event.event == "project_updated":
            await db.project_metrics.update_one(
                {"project_id": project_event.project_id, "user_id": project_event.user_id},
                {"$set": {"project_name": project_event.name or f"Project {project_event.project_id}", "last_activity": project_event.timestamp, "updated_at": datetime.now(timezone.utc)}},
            )
        elif project_event.event == "project_deleted":
            await db.project_metrics.delete_one({"project_id": project_event.project_id, "user_id": project_event.user_id})