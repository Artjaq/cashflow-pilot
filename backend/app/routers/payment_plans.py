import uuid

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.payment_plan import PaymentPlan
from app.schemas.payment_plan import PaymentPlanCreate, PaymentPlanRead, PaymentPlanUpdate

router = APIRouter(prefix="/payment-plans", tags=["payment-plans"])


def _compute_end_month(start_month, installments: int):
    return start_month + relativedelta(months=installments - 1)


@router.get("", response_model=list[PaymentPlanRead])
async def list_payment_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentPlan))
    return result.scalars().all()


@router.get("/{item_id}", response_model=PaymentPlanRead)
async def get_payment_plan(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(PaymentPlan, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


@router.post("", response_model=PaymentPlanRead, status_code=status.HTTP_201_CREATED)
async def create_payment_plan(payload: PaymentPlanCreate, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    if data.get("end_month") is None:
        data["end_month"] = _compute_end_month(data["start_month"], data["installments"])
    item = PaymentPlan(**data)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=PaymentPlanRead)
async def update_payment_plan(
    item_id: uuid.UUID, payload: PaymentPlanUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(PaymentPlan, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    if "start_month" in updates or "installments" in updates:
        if "end_month" not in updates:
            item.end_month = _compute_end_month(item.start_month, item.installments)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_plan(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(PaymentPlan, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await db.delete(item)
    await db.commit()
