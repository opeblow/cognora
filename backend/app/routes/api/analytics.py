from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.services.analytics_service import AnalyticsService
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=dict)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    try:
        return service.get_dashboard(str(current_user.id))
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/overview", response_model=dict)
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    try:
        return service.get_analytics(str(current_user.id))
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/accuracy-trends", response_model=dict)
def get_accuracy_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    try:
        analytics = service.get_analytics(str(current_user.id))
        return {"trends": analytics.get("accuracy_trends", [])}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/topic-mastery", response_model=dict)
def get_topic_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    try:
        analytics = service.get_analytics(str(current_user.id))
        return {"mastery": analytics.get("topic_mastery", [])}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))
