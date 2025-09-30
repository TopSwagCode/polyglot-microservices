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