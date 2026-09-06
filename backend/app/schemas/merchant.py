import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MerchantBase(BaseModel):
    name: str = Field(max_length=100)
    default_category_id: uuid.UUID | None = None
    email_domain_pattern: str | None = Field(default=None, max_length=100)


class MerchantCreate(MerchantBase):
    pass


class MerchantUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    default_category_id: uuid.UUID | None = None
    email_domain_pattern: str | None = Field(default=None, max_length=100)


class MerchantRead(MerchantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
