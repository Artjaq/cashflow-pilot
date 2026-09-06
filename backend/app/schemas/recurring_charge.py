import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RecurringChargeFrequency = Literal["monthly", "yearly"]


class RecurringChargeBase(BaseModel):
    label: str = Field(max_length=100)
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    category_id: uuid.UUID
    active_from: date
    active_until: date | None = None
    frequency: RecurringChargeFrequency = "monthly"


class RecurringChargeCreate(RecurringChargeBase):
    pass


class RecurringChargeUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=100)
    amount: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    category_id: uuid.UUID | None = None
    active_from: date | None = None
    active_until: date | None = None
    frequency: RecurringChargeFrequency | None = None


class RecurringChargeRead(RecurringChargeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
