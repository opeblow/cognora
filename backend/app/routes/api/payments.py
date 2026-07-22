import logging
import hashlib
import hmac
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.paystack_service import PaystackService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


class InitiatePurchaseRequest(BaseModel):
    credit_amount: int


class InitiatePurchaseResponse(BaseModel):
    authorization_url: str
    reference: str
    credit_amount: int
    amount: int
    currency: str


@router.get("/packs", response_model=dict)
def get_credit_packs():
    return {"packs": PaystackService.get_credit_packs()}


@router.post("/purchase/initiate", response_model=InitiatePurchaseResponse)
def initiate_purchase(
    request: InitiatePurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paystack = PaystackService(db)
    try:
        result = paystack.initialize_purchase(
            user_id=str(current_user.id),
            email=current_user.email,
            credit_amount=request.credit_amount,
        )
        return InitiatePurchaseResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Purchase initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment initiation failed")


@router.post("/webhook", response_model=dict)
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    secret = PaystackService.get_webhook_secret()
    if not secret:
        logger.error("PAYSTACK_SECRET_KEY is not configured — webhook validation disabled")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    expected = hmac.new(secret.encode(), raw_body, digestmod=hashlib.sha512).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        payload = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    paystack = PaystackService(db)
    try:
        success = paystack.handle_webhook(payload)
        if success:
            return {"status": "ok"}
        return {"status": "ignored"}
    except Exception:
        db.rollback()
        logger.exception("Webhook handling failed")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/verify/{reference}", response_model=dict)
def verify_payment(
    reference: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paystack = PaystackService(db)
    if not paystack.get_payment_for_user(reference, str(current_user.id)):
        raise HTTPException(status_code=404, detail="Transaction not found")
    result = paystack.verify_transaction(reference)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found or not completed")
    return {
        "status": result.get("status"),
        "amount": result.get("amount", 0) / 100,
        "currency": result.get("currency", "NGN"),
        "reference": reference,
    }
