from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import async_session_maker
from app.routers import budgets, categories, loans, merchants, payment_plans, recurring_charges, transactions
from app.seed import seed_categories


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with async_session_maker() as session:
        await seed_categories(session)
    yield


app = FastAPI(title="CashFlow-Pilot API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api/v1"
app.include_router(transactions.router, prefix=api_prefix)
app.include_router(categories.router, prefix=api_prefix)
app.include_router(merchants.router, prefix=api_prefix)
app.include_router(payment_plans.router, prefix=api_prefix)
app.include_router(recurring_charges.router, prefix=api_prefix)
app.include_router(budgets.router, prefix=api_prefix)
app.include_router(loans.router, prefix=api_prefix)
app.include_router(loans.repayments_router, prefix=api_prefix)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
