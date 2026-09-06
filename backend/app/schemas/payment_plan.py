import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentPlanBase(BaseModel):
    creditor: str = Field(max_length=100)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    installments: int = Field(gt=0)
    start_month: date
    end_month: date | None = None
    transaction_id: uuid.UUID | None = None


class PaymentPlanCreate(PaymentPlanBase):
    pass


class PaymentPlanUpdate(BaseModel):
    creditor: str | None = Field(default=None, max_length=100)
    total_amount: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    installments: int | None = Field(default=None, gt=0)
    start_month: date | None = None
    end_month: date | None = None
    transaction_id: uuid.UUID | None = None


class PaymentPlanRead(PaymentPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    monthly_amount: Decimal
    created_at: datetime
    updated_at: datetime
