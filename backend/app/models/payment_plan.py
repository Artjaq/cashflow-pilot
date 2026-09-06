import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Computed, Date, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PaymentPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_plans"
    __table_args__ = (
        CheckConstraint("installments > 0", name="ck_payment_plans_installments_positive"),
    )

    creditor: Mapped[str] = mapped_column(String(100), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    installments: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    monthly_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        Computed("total_amount / installments", persisted=True),
    )
    start_month: Mapped[date] = mapped_column(Date, nullable=False)
    end_month: Mapped[date | None] = mapped_column(Date, nullable=True)
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True
    )
