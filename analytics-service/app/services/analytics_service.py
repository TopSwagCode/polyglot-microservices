from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import structlog
from app.database import get_database
from app.models import TaskEvent, ProjectEvent, UserMetrics, ProjectMetrics

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self):
        self.db = None

    def _get_db(self):
        """Get database instance"""
        if not self.db:
            self.db = get_database()
        return self.db

    async def update_task_metrics(self, task_event: TaskEvent):
        """Update user and project metrics based on task event"""
        try:
            db = self._get_db()
            
            # Update user metrics
            await self._update_user_metrics(task_event)
            
            # Update project metrics
            await self._update_project_metrics_from_task(task_event)
            
            logger.debug("Task metrics updated", 
                        task_id=task_event.task_id,
                        user_id=task_event.user_id,
                        event=task_event.event)
            
        except Exception as e:
            logger.error("Error updating task metrics", error=str(e))

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
                        event=project_event.event)
            
        except Exception as e:
            logger.error("Error updating project metrics", error=str(e))

    async def _update_user_metrics(self, task_event: TaskEvent):
        """Update user-level metrics"""
        db = self._get_db()
        
        # Get or create user metrics
        user_metrics = await db.user_metrics.find_one({"user_id": task_event.user_id})
        
        if not user_metrics:
            user_metrics = UserMetrics(
                user_id=task_event.user_id,
                username=task_event.username
            ).model_dump()

        # Update metrics based on event type
        if task_event.event == "task_created":
            user_metrics["total_tasks"] += 1
        elif task_event.event == "task_completed":
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
        db = self._get_db()
        
        # Get or create project metrics
        project_metrics = await db.project_metrics.find_one({
            "project_id": task_event.project_id,
            "user_id": task_event.user_id
        })
        
        if not project_metrics:
            project_metrics = ProjectMetrics(
                project_id=task_event.project_id,
                user_id=task_event.user_id,
                username=task_event.username,
                project_name=f"Project {task_event.project_id}",
                created_at_project=task_event.timestamp
            ).model_dump()

        # Update metrics based on event type
        if task_event.event == "task_created":
            project_metrics["total_tasks"] += 1
        elif task_event.event == "task_completed":
            project_metrics["completed_tasks"] += 1
        elif task_event.event_type == "deleted":
            project_metrics["total_tasks"] = max(0, project_metrics["total_tasks"] - 1)
            if task_event.task_data.get("completed"):
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

    async def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get dashboard metrics for a user"""
        db = self._get_db()
        
        # Get user metrics
        user_metrics = await db.user_metrics.find_one({"user_id": user_id})
        if not user_metrics:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "active_projects": 0,
                "completion_rate": 0.0,
                "recent_activity": []
            }

        # Get recent activity (last 10 events)
        recent_events = await db.task_events.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(10).to_list(10)

        recent_activity = [
            {
                "type": "task",
                "event": event["event"],
                "task_id": event["task_id"],
                "project_id": event["project_id"],
                "timestamp": event["timestamp"].isoformat()
            }
            for event in recent_events
        ]

        return {
            "total_tasks": user_metrics["total_tasks"],
            "completed_tasks": user_metrics["completed_tasks"],
            "active_projects": user_metrics["active_projects"],
            "completion_rate": user_metrics["completion_rate"],
            "recent_activity": recent_activity
        }

    async def get_project_analytics(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Get analytics for a specific project"""
        db = self._get_db()
        
        # Get project metrics
        project_metrics = await db.project_metrics.find_one({
            "project_id": project_id,
            "user_id": user_id
        })
        
        if not project_metrics:
            return None

        # Get task events for timeline
        task_events = await db.task_events.find(
            {"project_id": project_id, "user_id": user_id}
        ).sort("timestamp", 1).to_list(100)

        # Build timeline
        timeline = [
            {
                "event_type": event["event_type"],
                "task_id": event["task_id"],
                "timestamp": event["timestamp"].isoformat(),
                "task_title": event["task_data"].get("title", "Task")
            }
            for event in task_events
        ]

        # Task distribution by status (simplified)
        task_distribution = {
            "completed": project_metrics["completed_tasks"],
            "pending": project_metrics["total_tasks"] - project_metrics["completed_tasks"]
        }

        return {
            "project_id": project_metrics["project_id"],
            "project_name": project_metrics["project_name"],
            "total_tasks": project_metrics["total_tasks"],
            "completed_tasks": project_metrics["completed_tasks"],
            "completion_rate": project_metrics["completion_rate"],
            "avg_completion_time_hours": project_metrics.get("avg_completion_time_hours"),
            "task_distribution": task_distribution,
            "timeline": timeline
        }

    async def get_task_summary(self, user_id: int) -> Dict[str, Any]:
        """Get task summary for a user"""
        db = self._get_db()
        
        user_metrics = await db.user_metrics.find_one({"user_id": user_id})
        if not user_metrics:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "completion_rate": 0.0,
                "tasks_by_status": {"completed": 0, "pending": 0},
                "recent_completions": []
            }

        pending_tasks = user_metrics["total_tasks"] - user_metrics["completed_tasks"]

        # Get recent completions
        recent_completions = await db.task_events.find(
            {"user_id": user_id, "event_type": "completed"}
        ).sort("timestamp", -1).limit(5).to_list(5)

        recent_completions_data = [
            {
                "task_id": event["task_id"],
                "project_id": event["project_id"],
                "title": event["task_data"].get("title", "Task"),
                "completed_at": event["timestamp"].isoformat()
            }
            for event in recent_completions
        ]

        return {
            "total_tasks": user_metrics["total_tasks"],
            "completed_tasks": user_metrics["completed_tasks"],
            "pending_tasks": pending_tasks,
            "completion_rate": user_metrics["completion_rate"],
            "tasks_by_status": {
                "completed": user_metrics["completed_tasks"],
                "pending": pending_tasks
            },
            "recent_completions": recent_completions_data
        }

    async def get_productivity_insights(self, user_id: int) -> Dict[str, Any]:
        """Get productivity insights for a user"""
        db = self._get_db()
        
        # Get task events from last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        task_events = await db.task_events.find({
            "user_id": user_id,
            "timestamp": {"$gte": thirty_days_ago},
            "event_type": "completed"
        }).to_list(1000)

        # Calculate daily completions
        daily_completions = defaultdict(int)
        for event in task_events:
            date_key = event["timestamp"].strftime("%Y-%m-%d")
            daily_completions[date_key] += 1

        # Calculate weekly summary
        total_completions = len(task_events)
        avg_daily = total_completions / 30 if total_completions > 0 else 0
        
        # Simple productivity score (0-100)
        productivity_score = min(100, avg_daily * 20)  # Scale appropriately
        
        # Generate recommendations
        recommendations = []
        if avg_daily < 1:
            recommendations.append("Try to complete at least one task per day")
        if productivity_score < 50:
            recommendations.append("Consider breaking larger tasks into smaller ones")
        if total_completions > 0:
            recommendations.append("Great job staying consistent!")

        return {
            "daily_completions": dict(daily_completions),
            "weekly_summary": {
                "total_completions": total_completions,
                "avg_daily_completions": round(avg_daily, 2),
                "most_productive_day": max(daily_completions.items(), key=lambda x: x[1])[0] if daily_completions else None
            },
            "productivity_score": round(productivity_score, 1),
            "recommendations": recommendations
        }