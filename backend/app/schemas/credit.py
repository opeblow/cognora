from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CreditTransactionResponse(BaseModel):
    id: str
    amount: str
    transaction_type: str
    description: Optional[str] = None
    created_at: datetime

    


class CreditBalanceResponse(BaseModel):
    credits: int
    weekly_credits_used: int
    weekly_credits_total: int
    transactions: list[CreditTransactionResponse]

