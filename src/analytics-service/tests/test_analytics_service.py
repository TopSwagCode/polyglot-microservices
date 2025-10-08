import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.services.analytics_service import AnalyticsService
from app.models import TaskEvent, ProjectEvent
from datetime import datetime, timezone


@pytest.fixture
def analytics_service():
    return AnalyticsService()


@pytest.fixture
def mock_db():
    db = Mock()
    db.user_metrics = Mock()
    db.project_metrics = Mock()
    db.task_events = Mock()
    db.project_events = Mock()
    return db


@pytest.fixture
def sample_task_event():
    return TaskEvent(
        event_type="created",
        task_id=1,
        project_id=1,
        user_id=1,
        username="testuser",
        task_data={"title": "Test Task", "description": "A test task"},
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_project_event():
    return ProjectEvent(
        event_type="created",
        project_id=1,
        user_id=1,
        username="testuser",
        project_data={"name": "Test Project", "description": "A test project"},
        timestamp=datetime.now(timezone.utc)
    )


class TestAnalyticsService:
    @pytest.mark.asyncio
    async def test_get_user_dashboard_no_data(self, analytics_service, mock_db, monkeypatch):
        """Test dashboard with no user data"""
        mock_db.user_metrics.find_one = AsyncMock(return_value=None)
        mock_db.task_events.find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_user_dashboard(1)
        
        assert result["total_tasks"] == 0
        assert result["completed_tasks"] == 0
        assert result["active_projects"] == 0
        assert result["completion_rate"] == 0.0
        assert result["recent_activity"] == []

    @pytest.mark.asyncio
    async def test_get_user_dashboard_with_data(self, analytics_service, mock_db, monkeypatch):
        """Test dashboard with user data"""
        user_metrics = {
            "total_tasks": 10,
            "completed_tasks": 7,
            "active_projects": 3,
            "completion_rate": 0.7
        }
        
        recent_events = [
            {
                "event_type": "completed",
                "task_id": 1,
                "project_id": 1,
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        mock_db.user_metrics.find_one = AsyncMock(return_value=user_metrics)
        mock_db.task_events.find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=recent_events)
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_user_dashboard(1)
        
        assert result["total_tasks"] == 10
        assert result["completed_tasks"] == 7
        assert result["active_projects"] == 3
        assert result["completion_rate"] == 0.7
        assert len(result["recent_activity"]) == 1

    @pytest.mark.asyncio
    async def test_get_task_summary(self, analytics_service, mock_db, monkeypatch):
        """Test task summary functionality"""
        user_metrics = {
            "total_tasks": 15,
            "completed_tasks": 10,
            "completion_rate": 0.667
        }
        
        recent_completions = [
            {
                "task_id": 1,
                "project_id": 1,
                "task_data": {"title": "Completed Task"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        mock_db.user_metrics.find_one = AsyncMock(return_value=user_metrics)
        mock_db.task_events.find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=recent_completions)
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_task_summary(1)
        
        assert result["total_tasks"] == 15
        assert result["completed_tasks"] == 10
        assert result["pending_tasks"] == 5
        assert result["completion_rate"] == 0.667
        assert result["tasks_by_status"]["completed"] == 10
        assert result["tasks_by_status"]["pending"] == 5

    @pytest.mark.asyncio
    async def test_get_project_analytics_not_found(self, analytics_service, mock_db, monkeypatch):
        """Test project analytics when project not found"""
        mock_db.project_metrics.find_one = AsyncMock(return_value=None)
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_project_analytics(1, 1)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_project_analytics_with_data(self, analytics_service, mock_db, monkeypatch):
        """Test project analytics with data"""
        project_metrics = {
            "project_id": 1,
            "project_name": "Test Project",
            "total_tasks": 8,
            "completed_tasks": 5,
            "completion_rate": 0.625,
            "avg_completion_time_hours": None
        }
        
        task_events = [
            {
                "event_type": "created",
                "task_id": 1,
                "task_data": {"title": "Task 1"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        mock_db.project_metrics.find_one = AsyncMock(return_value=project_metrics)
        mock_db.task_events.find.return_value.sort.return_value.to_list = AsyncMock(return_value=task_events)
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_project_analytics(1, 1)
        
        assert result["project_id"] == 1
        assert result["project_name"] == "Test Project"
        assert result["total_tasks"] == 8
        assert result["completed_tasks"] == 5
        assert result["completion_rate"] == 0.625
        assert result["task_distribution"]["completed"] == 5
        assert result["task_distribution"]["pending"] == 3

    @pytest.mark.asyncio
    async def test_get_productivity_insights(self, analytics_service, mock_db, monkeypatch):
        """Test productivity insights calculation"""
        task_events = [
            {
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        mock_db.task_events.find.return_value.to_list = AsyncMock(return_value=task_events)
        
        monkeypatch.setattr(analytics_service, '_get_db', lambda: mock_db)
        
        result = await analytics_service.get_productivity_insights(1)
        
        assert "daily_completions" in result
        assert "weekly_summary" in result
        assert "productivity_score" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)