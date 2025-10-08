import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user


@pytest.fixture 
def client():
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    return {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }


@pytest.fixture
def mock_analytics_service():
    service = Mock()
    service.get_user_dashboard = AsyncMock(return_value={
        "total_tasks": 5,
        "completed_tasks": 3,
        "active_projects": 2,
        "completion_rate": 0.6,
        "recent_activity": []
    })
    service.get_task_summary = AsyncMock(return_value={
        "total_tasks": 5,
        "completed_tasks": 3,
        "pending_tasks": 2,
        "completion_rate": 0.6,
        "tasks_by_status": {"completed": 3, "pending": 2},
        "recent_completions": []
    })
    service.get_productivity_insights = AsyncMock(return_value={
        "daily_completions": {"2024-01-01": 2},
        "weekly_summary": {"total_completions": 2, "avg_daily_completions": 0.29},
        "productivity_score": 5.8,
        "recommendations": ["Try to complete at least one task per day"]
    })
    service.get_project_analytics = AsyncMock(return_value={
        "project_id": 1,
        "project_name": "Test Project",
        "total_tasks": 3,
        "completed_tasks": 2,
        "completion_rate": 0.67,
        "avg_completion_time_hours": None,
        "task_distribution": {"completed": 2, "pending": 1},
        "timeline": []
    })
    return service


class TestAnalyticsAPI:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "analytics-service"}

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Analytics Service"
        assert "version" in data
        assert "docs" in data

    def test_dashboard_unauthorized(self, client):
        """Test dashboard endpoint without authentication"""
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_dashboard_with_auth(self, client, mock_current_user, mock_analytics_service, monkeypatch):
        """Test dashboard endpoint with authentication"""
        # Mock the auth dependency
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        # Mock the analytics service
        from app.api.analytics import analytics_service
        monkeypatch.setattr("app.api.analytics.analytics_service", mock_analytics_service)
        
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_tasks"] == 5
        assert data["completed_tasks"] == 3
        assert data["completion_rate"] == 0.6
        
        # Clean up
        app.dependency_overrides.clear()

    def test_task_summary_with_auth(self, client, mock_current_user, mock_analytics_service, monkeypatch):
        """Test task summary endpoint with authentication"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        monkeypatch.setattr("app.api.analytics.analytics_service", mock_analytics_service)
        
        response = client.get("/api/v1/analytics/tasks/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_tasks"] == 5
        assert data["pending_tasks"] == 2
        
        app.dependency_overrides.clear()

    def test_productivity_with_auth(self, client, mock_current_user, mock_analytics_service, monkeypatch):
        """Test productivity endpoint with authentication"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        monkeypatch.setattr("app.api.analytics.analytics_service", mock_analytics_service)
        
        response = client.get("/api/v1/analytics/productivity")
        assert response.status_code == 200
        
        data = response.json()
        assert "productivity_score" in data
        assert "recommendations" in data
        
        app.dependency_overrides.clear()

    def test_project_analytics_with_auth(self, client, mock_current_user, mock_analytics_service, monkeypatch):
        """Test project analytics endpoint with authentication"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        monkeypatch.setattr("app.api.analytics.analytics_service", mock_analytics_service)
        
        response = client.get("/api/v1/analytics/projects/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["project_id"] == 1
        assert data["project_name"] == "Test Project"
        
        app.dependency_overrides.clear()

    def test_project_analytics_not_found(self, client, mock_current_user, monkeypatch):
        """Test project analytics endpoint when project not found"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        mock_service = Mock()
        mock_service.get_project_analytics = AsyncMock(return_value=None)
        monkeypatch.setattr("app.api.analytics.analytics_service", mock_service)
        
        response = client.get("/api/v1/analytics/projects/999")
        assert response.status_code == 404
        
        app.dependency_overrides.clear()