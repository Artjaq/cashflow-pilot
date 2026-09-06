import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    category_id: uuid.UUID
    monthly_limit: Decimal = Field(max_digits=10, decimal_places=2)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    monthly_limit: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)


class BudgetRead(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
