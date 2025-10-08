from datetime import datetime, timezone
from typing import Dict, Any
import structlog
from app.database import get_database
from app.models import TaskEvent, ProjectEvent, UserMetrics, ProjectMetrics

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self):
        self.db = None

    def _get_db(self):
        """Get database instance"""
        if self.db is None:
            self.db = get_database()
        return self.db

    async def update_task_metrics(self, task_event: TaskEvent):
        """Update user and project metrics based on task event"""
        try:
            # Update user metrics
            await self._update_user_metrics(task_event)
            
            # Update project metrics
            await self._update_project_metrics_from_task(task_event)
            
            logger.debug("Task metrics updated", 
                        task_id=task_event.task_id,
                        user_id=task_event.user_id,
                        event_type=task_event.event)
            
        except Exception as e:
            logger.error("Error updating task metrics", 
                        error=str(e), 
                        task_id=getattr(task_event, 'task_id', None),
                        user_id=getattr(task_event, 'user_id', None),
                        event_type=getattr(task_event, 'event', None),
                        exc_info=True)

    async def update_project_metrics(self, project_event: ProjectEvent):
        """Update metrics based on project event"""
        try:
            # Update user's active project count
            await self._update_user_project_count(project_event)
            
            # Update project metrics document
            await self._update_project_metrics_from_project(project_event)
            
            logger.debug("Project metrics updated",
                        project_id=project_event.project_id,
                        user_id=project_event.user_id,
                        event_type=project_event.event)
            
        except Exception as e:
            logger.error("Error updating project metrics", 
                        error=str(e),
                        project_id=getattr(project_event, 'project_id', None),
                        user_id=getattr(project_event, 'user_id', None),
                        event_type=getattr(project_event, 'event', None),
                        exc_info=True)

    async def _update_user_metrics(self, task_event: TaskEvent):
        """Update user-level metrics"""
        db = self._get_db()
        
        # Get or create user metrics
        user_metrics = await db.user_metrics.find_one({"user_id": task_event.user_id})
        
        if user_metrics is None:
            logger.info("Creating new user metrics", user_id=task_event.user_id, username=task_event.username)
            user_metrics = UserMetrics(
                user_id=task_event.user_id,
                username=task_event.username
            ).model_dump()
            logger.debug("Created user metrics structure", keys=list(user_metrics.keys()))
        else:
            logger.debug("Found existing user metrics", user_id=task_event.user_id)
            # Ensure all required keys exist for backwards compatibility
            if "total_tasks" not in user_metrics:
                user_metrics["total_tasks"] = 0
            if "completed_tasks" not in user_metrics:
                user_metrics["completed_tasks"] = 0
            if "completion_rate" not in user_metrics:
                user_metrics["completion_rate"] = 0.0

        # Update metrics based on event type
        if task_event.event == "task_created":
            user_metrics["total_tasks"] += 1
        elif task_event.event == "task_updated" and task_event.status == "completed":
            user_metrics["completed_tasks"] += 1
        elif task_event.event == "task_deleted":
            user_metrics["total_tasks"] = max(0, user_metrics["total_tasks"] - 1)
            # Adjust completed count if the deleted task was completed
            if task_event.status == "completed":
                user_metrics["completed_tasks"] = max(0, user_metrics["completed_tasks"] - 1)

        # Calculate completion rate
        if user_metrics["total_tasks"] > 0:
            user_metrics["completion_rate"] = user_metrics["completed_tasks"] / user_metrics["total_tasks"]
        else:
            user_metrics["completion_rate"] = 0.0

        # Update last activity
        user_metrics["last_activity"] = task_event.timestamp
        user_metrics["updated_at"] = datetime.now(timezone.utc)

        # Upsert user metrics
        await db.user_metrics.replace_one(
            {"user_id": task_event.user_id},
            user_metrics,
            upsert=True
        )

    async def _update_project_metrics_from_task(self, task_event: TaskEvent):
        """Update project-level metrics from task event"""
        if not task_event.project_id:
            return
            
        db = self._get_db()
        
        # Get or create project metrics
        project_metrics = await db.project_metrics.find_one({
            "project_id": task_event.project_id,
            "user_id": task_event.user_id
        })
        
        if project_metrics is None:
            logger.info("Creating new project metrics", 
                       project_id=task_event.project_id, 
                       user_id=task_event.user_id)
            project_metrics = ProjectMetrics(
                project_id=task_event.project_id,
                user_id=task_event.user_id,
                username=task_event.username,
                project_name=f"Project {task_event.project_id}",
                created_at_project=task_event.timestamp
            ).model_dump()
        else:
            logger.debug("Found existing project metrics", 
                        project_id=task_event.project_id,
                        user_id=task_event.user_id)
            # Ensure all required keys exist for backwards compatibility
            if "total_tasks" not in project_metrics:
                project_metrics["total_tasks"] = 0
            if "completed_tasks" not in project_metrics:
                project_metrics["completed_tasks"] = 0
            if "completion_rate" not in project_metrics:
                project_metrics["completion_rate"] = 0.0

        # Update metrics based on event type
        if task_event.event == "task_created":
            project_metrics["total_tasks"] += 1
        elif task_event.event == "task_updated" and task_event.status == "completed":
            project_metrics["completed_tasks"] += 1
        elif task_event.event == "task_deleted":
            project_metrics["total_tasks"] = max(0, project_metrics["total_tasks"] - 1)
            if task_event.status == "completed":
                project_metrics["completed_tasks"] = max(0, project_metrics["completed_tasks"] - 1)

        # Calculate completion rate
        if project_metrics["total_tasks"] > 0:
            project_metrics["completion_rate"] = project_metrics["completed_tasks"] / project_metrics["total_tasks"]
        else:
            project_metrics["completion_rate"] = 0.0

        # Update last activity
        project_metrics["last_activity"] = task_event.timestamp
        project_metrics["updated_at"] = datetime.now(timezone.utc)

        # Upsert project metrics
        await db.project_metrics.replace_one(
            {"project_id": task_event.project_id, "user_id": task_event.user_id},
            project_metrics,
            upsert=True
        )

    async def _update_user_project_count(self, project_event: ProjectEvent):
        """Update user's active project count"""
        db = self._get_db()
        
        # Count active projects for user
        active_projects = await db.project_metrics.count_documents({"user_id": project_event.user_id})
        
        # Update user metrics
        await db.user_metrics.update_one(
            {"user_id": project_event.user_id},
            {
                "$set": {
                    "active_projects": active_projects,
                    "last_activity": project_event.timestamp,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )

    async def _update_project_metrics_from_project(self, project_event: ProjectEvent):
        """Update project metrics from project event"""
        db = self._get_db()
        
        if project_event.event == "project_created":
            # Create new project metrics document
            project_metrics = ProjectMetrics(
                project_id=project_event.project_id,
                user_id=project_event.user_id,
                username=project_event.username,
                project_name=project_event.name or f"Project {project_event.project_id}",
                created_at_project=project_event.timestamp
            )
            
            await db.project_metrics.insert_one(project_metrics.model_dump())
            
        elif project_event.event == "project_updated":
            # Update project name if changed
            await db.project_metrics.update_one(
                {"project_id": project_event.project_id, "user_id": project_event.user_id},
                {
                    "$set": {
                        "project_name": project_event.name or f"Project {project_event.project_id}",
                        "last_activity": project_event.timestamp,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
        elif project_event.event == "project_deleted":
            # Remove project metrics
            await db.project_metrics.delete_one({
                "project_id": project_event.project_id,
                "user_id": project_event.user_id
            })