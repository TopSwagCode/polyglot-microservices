from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
import structlog
from app.auth import get_admin_user
from app.services.analytics_service import AnalyticsService
from app.models import (
    DashboardResponse,
    ProjectAnalyticsResponse,
    TaskSummaryResponse,
    ProductivityResponse
)

logger = structlog.get_logger()

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(request: Request, current_user: dict = Depends(get_admin_user)):
    """Get user dashboard metrics"""
    try:
        dashboard_data = await analytics_service.get_user_dashboard(current_user["user_id"])
        return DashboardResponse(**dashboard_data)
    except Exception as e:
        logger.error("Error getting dashboard", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )


@router.get("/projects/{project_id}", response_model=ProjectAnalyticsResponse)
async def get_project_analytics(
    project_id: int,
    request: Request,
    current_user: dict = Depends(get_admin_user)
):
    """Get analytics for a specific project"""
    try:
        project_data = await analytics_service.get_project_analytics(
            project_id, current_user["user_id"]
        )
        
        if project_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
        return ProjectAnalyticsResponse(**project_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting project analytics", 
                    error=str(e), 
                    user_id=current_user["user_id"],
                    project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project analytics"
        )


@router.get("/tasks/summary", response_model=TaskSummaryResponse)
async def get_task_summary(request: Request, current_user: dict = Depends(get_admin_user)):
    """Get task completion metrics summary"""
    try:
        summary_data = await analytics_service.get_task_summary(current_user["user_id"])
        return TaskSummaryResponse(**summary_data)
    except Exception as e:
        logger.error("Error getting task summary", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task summary"
        )


@router.get("/productivity", response_model=ProductivityResponse)
async def get_productivity_insights(request: Request, current_user: dict = Depends(get_admin_user)):
    """Get user productivity insights and recommendations"""
    try:
        productivity_data = await analytics_service.get_productivity_insights(current_user["user_id"])
        return ProductivityResponse(**productivity_data)
    except Exception as e:
        logger.error("Error getting productivity insights", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve productivity insights"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "analytics-service"}