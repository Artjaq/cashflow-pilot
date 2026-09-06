import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Transaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("kind IN ('expense', 'income')", name="ck_transactions_kind"),
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "status IN ('pending', 'settled', 'installment')", name="ck_transactions_status"
        ),
        CheckConstraint(
            "recurrence IN ('recurring', 'one_off', 'installment')",
            name="ck_transactions_recurrence",
        ),
        CheckConstraint(
            "priority IS NULL OR priority BETWEEN 1 AND 5", name="ck_transactions_priority_range"
        ),
    )

    kind: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=True
    )
    payment_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default=text("'pending'")
    )
    priority: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    recurrence: Mapped[str] = mapped_column(
        String(20), nullable=False, default="one_off", server_default=text("'one_off'")
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    settled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
