import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TransactionKind = Literal["expense", "income"]
TransactionStatus = Literal["pending", "settled", "installment"]
TransactionRecurrence = Literal["recurring", "one_off", "installment"]


class TransactionBase(BaseModel):
    kind: TransactionKind
    due_date: date | None = None
    description: str = Field(max_length=255)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category_id: uuid.UUID
    merchant_id: uuid.UUID | None = None
    payment_method: str | None = Field(default=None, max_length=100)
    status: TransactionStatus = "pending"
    priority: int | None = Field(default=None, ge=1, le=5)
    recurrence: TransactionRecurrence = "one_off"
    notes: str | None = None
    settled_date: date | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    kind: TransactionKind | None = None
    due_date: date | None = None
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category_id: uuid.UUID | None = None
    merchant_id: uuid.UUID | None = None
    payment_method: str | None = Field(default=None, max_length=100)
    status: TransactionStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    recurrence: TransactionRecurrence | None = None
    notes: str | None = None
    settled_date: date | None = None


class TransactionRead(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
