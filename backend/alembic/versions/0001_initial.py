"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_WITH_UPDATED_AT = [
    "categories",
    "merchants",
    "transactions",
    "payment_plans",
    "recurring_charges",
    "budgets",
    "loans",
    "loan_repayments",
]


def _id_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )

    op.create_table(
        "categories",
        _id_column(),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("kind", sa.String(20), nullable=False),
        *_timestamp_columns(),
        sa.CheckConstraint("kind IN ('expense', 'income')", name="ck_categories_kind"),
    )

    op.create_table(
        "merchants",
        _id_column(),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column(
            "default_category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=True,
        ),
        sa.Column("email_domain_pattern", sa.String(100), nullable=True),
        *_timestamp_columns(),
    )

    op.create_table(
        "transactions",
        _id_column(),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column(
            "merchant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("merchants.id"),
            nullable=True,
        ),
        sa.Column("payment_method", sa.String(100), nullable=True),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default=sa.text("'pending'")
        ),
        sa.Column("priority", sa.SmallInteger(), nullable=True),
        sa.Column(
            "recurrence", sa.String(20), nullable=False, server_default=sa.text("'one_off'")
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("settled_date", sa.Date(), nullable=True),
        *_timestamp_columns(),
        sa.CheckConstraint("kind IN ('expense', 'income')", name="ck_transactions_kind"),
        sa.CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        sa.CheckConstraint(
            "status IN ('pending', 'settled', 'installment')", name="ck_transactions_status"
        ),
        sa.CheckConstraint(
            "recurrence IN ('recurring', 'one_off', 'installment')",
            name="ck_transactions_recurrence",
        ),
        sa.CheckConstraint(
            "priority IS NULL OR priority BETWEEN 1 AND 5",
            name="ck_transactions_priority_range",
        ),
    )

    op.create_table(
        "payment_plans",
        _id_column(),
        sa.Column("creditor", sa.String(100), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("installments", sa.SmallInteger(), nullable=False),
        sa.Column(
            "monthly_amount",
            sa.Numeric(10, 2),
            sa.Computed("total_amount / installments", persisted=True),
            nullable=True,
        ),
        sa.Column("start_month", sa.Date(), nullable=False),
        sa.Column("end_month", sa.Date(), nullable=True),
        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transactions.id"),
            nullable=True,
        ),
        *_timestamp_columns(),
        sa.CheckConstraint("installments > 0", name="ck_payment_plans_installments_positive"),
    )

    op.create_table(
        "recurring_charges",
        _id_column(),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_until", sa.Date(), nullable=True),
        sa.Column(
            "frequency", sa.String(20), nullable=False, server_default=sa.text("'monthly'")
        ),
        *_timestamp_columns(),
        sa.CheckConstraint(
            "frequency IN ('monthly', 'yearly')", name="ck_recurring_charges_frequency"
        ),
    )

    op.create_table(
        "budgets",
        _id_column(),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column("monthly_limit", sa.Numeric(10, 2), nullable=False),
        *_timestamp_columns(),
    )

    op.create_table(
        "loans",
        _id_column(),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        *_timestamp_columns(),
    )

    op.create_table(
        "loan_repayments",
        _id_column(),
        sa.Column(
            "loan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False
        ),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *_timestamp_columns(),
    )

    for table in TABLES_WITH_UPDATED_AT:
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at()
            """
        )


def downgrade() -> None:
    for table in TABLES_WITH_UPDATED_AT:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table}")

    op.drop_table("loan_repayments")
    op.drop_table("loans")
    op.drop_table("budgets")
    op.drop_table("recurring_charges")
    op.drop_table("payment_plans")
    op.drop_table("transactions")
    op.drop_table("merchants")
    op.drop_table("categories")

    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
