import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LoanBase(BaseModel):
    label: str = Field(max_length=100)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=100)
    total_amount: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)


class LoanRead(LoanBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LoanRepaymentBase(BaseModel):
    loan_id: uuid.UUID
    payment_date: date
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    notes: str | None = None


class LoanRepaymentCreate(LoanRepaymentBase):
    pass


class LoanRepaymentUpdate(BaseModel):
    loan_id: uuid.UUID | None = None
    payment_date: date | None = None
    amount: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    notes: str | None = None


class LoanRepaymentRead(LoanRepaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
