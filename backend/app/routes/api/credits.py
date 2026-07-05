from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.services.credit_service import CreditService
from app.services.credit_policy import TrialCreditPolicy, PaidCreditPolicy
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/credits", tags=["Credits"])


class PurchaseCreditsRequest(BaseModel):
    amount: int
    reference: Optional[str] = None


class UpgradeRequest(BaseModel):
    plan: str = "paid"


@router.get("/balance", response_model=dict)
def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CreditService(db)
    return service.get_balance(str(current_user.id))


@router.post("/purchase", response_model=dict)
def purchase_credits(
    request: PurchaseCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    service = CreditService(db)
    try:
        service.add_credits(
            user_id=str(current_user.id),
            amount=request.amount,
            description=f"Purchased {request.amount} credits (ref: {request.reference or 'direct'})",
        )
        return {
            "message": f"{request.amount} credits added",
            "balance": service.get_balance(str(current_user.id)),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upgrade", response_model=dict)
def upgrade_to_premium(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade from trial to paid plan (or vice versa)."""
    service = CreditService(db)

    if request.plan == "paid":
        service.set_policy(PaidCreditPolicy())
        return {"message": "Upgraded to paid plan", "plan": "paid"}
    elif request.plan == "trial":
        service.set_policy(TrialCreditPolicy())
        return {"message": "Switched to trial plan", "plan": "trial"}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {request.plan}")


@router.get("/costs", response_model=dict)
def get_credit_costs(
    current_user: User = Depends(get_current_user),
):
    return {
        "costs": {
            "ai_ask": 1,
            "generate_quiz": 2,
            "mock_exam": 10,
        }
    }
