import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional

from app.core.platforms import PLATFORMS


class DebtCreate(BaseModel):
    platform: str = Field(..., max_length=100)
    amount: int = Field(..., gt=0)
    due_date: date
    interest_rate: Optional[float] = None
    interest_type: Optional[str] = None
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_installments(self):
        cur = self.installment_current
        tot = self.installment_total
        if cur is not None and tot is not None:
            if cur < 1 or tot < 1:
                raise ValueError("installment_current and installment_total must be >= 1")
            if cur > tot:
                raise ValueError("installment_current cannot exceed installment_total")
        return self


class DebtResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    amount: int
    due_date: date
    interest_rate: Optional[float] = None
    interest_type: Optional[str] = None
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlatformRateResponse(BaseModel):
    model_config = {"from_attributes": True}
    platform: str
    avg_rate: float
    common_type: str | None
    sample_count: int
    confidence: float


class MonthlySummary(BaseModel):
    total_active: int
    total_amount: int
    paid_this_month: int
    paid_amount: int
    upcoming: list[DebtResponse]
