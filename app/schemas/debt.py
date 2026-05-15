import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional


class DebtCreate(BaseModel):
    platform: str = Field(..., max_length=100)
    amount: int = Field(..., ge=0)
    due_date: date
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class DebtResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    amount: int
    due_date: date
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MonthlySummary(BaseModel):
    total_active: int
    total_amount: int
    paid_this_month: int
    paid_amount: int
    upcoming: list[DebtResponse]
