from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.services.credit_service import CreditService
from app.models.user import User

router = APIRouter(prefix="/credits", tags=["Credits"])


@router.get("/balance", response_model=dict)
def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CreditService(db)
    return service.get_balance(str(current_user.id))
