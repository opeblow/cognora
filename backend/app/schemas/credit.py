from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CreditTransactionResponse(BaseModel):
    id: str
    amount: int
    transaction_type: str
    description: Optional[str] = None
    created_at: datetime


class CreditBalanceResponse(BaseModel):
    plan: str = "trial"
    credits: int
    weekly_credits_used: int = 0
    weekly_credits_total: int = 0
    is_trial: bool = True
    transactions: list[CreditTransactionResponse]


class PurchaseCreditsRequest(BaseModel):
    amount: int
    reference: Optional[str] = None
