import uuid
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.transaction import Transaction
from app.schemas.pagination import Page
from app.schemas.transaction import (
    TransactionCreate,
    TransactionKind,
    TransactionRead,
    TransactionRecurrence,
    TransactionStatus,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=Page[TransactionRead])
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    kind: TransactionKind | None = None,
    status_filter: TransactionStatus | None = Query(default=None, alias="status"),
    category: uuid.UUID | None = None,
    recurrence: TransactionRecurrence | None = None,
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    query = select(Transaction)

    if kind is not None:
        query = query.where(Transaction.kind == kind)
    if status_filter is not None:
        query = query.where(Transaction.status == status_filter)
    if category is not None:
        query = query.where(Transaction.category_id == category)
    if recurrence is not None:
        query = query.where(Transaction.recurrence == recurrence)
    if month is not None:
        month_start = datetime.strptime(month, "%Y-%m").date().replace(day=1)
        month_end = month_start + relativedelta(months=1)
        query = query.where(
            Transaction.due_date >= month_start, Transaction.due_date < month_end
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    query = query.order_by(Transaction.due_date.desc().nulls_last()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: TransactionCreate, db: AsyncSession = Depends(get_db)):
    item = Transaction(**payload.model_dump())
    db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc.orig)) from exc
    await db.refresh(item)
    return item


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: uuid.UUID, payload: TransactionUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc.orig)) from exc
    await db.refresh(item)
    return item


@router.patch("/{transaction_id}/settle", response_model=TransactionRead)
async def settle_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    item.status = "settled"
    if item.settled_date is None:
        item.settled_date = date.today()
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await db.delete(item)
    await db.commit()
