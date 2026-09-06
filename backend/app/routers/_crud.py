import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base, get_db


def build_crud_router(
    *,
    model: type[Base],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    prefix: str,
    tags: list[str],
) -> APIRouter:
    """Fabrique un router CRUD standard pour une ressource simple (sans filtres/pagination)."""

    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=list[read_schema])
    async def list_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(model))
        return result.scalars().all()

    @router.get("/{item_id}", response_model=read_schema)
    async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        item = await db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return item

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(payload: create_schema, db: AsyncSession = Depends(get_db)):
        item = model(**payload.model_dump())
        db.add(item)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc.orig)) from exc
        await db.refresh(item)
        return item

    @router.put("/{item_id}", response_model=read_schema)
    async def update_item(
        item_id: uuid.UUID, payload: update_schema, db: AsyncSession = Depends(get_db)
    ):
        item = await db.get(model, item_id)
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

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        item = await db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        await db.delete(item)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc.orig)) from exc

    return router
