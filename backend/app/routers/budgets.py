from app.models.budget import Budget
from app.routers._crud import build_crud_router
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate

router = build_crud_router(
    model=Budget,
    create_schema=BudgetCreate,
    update_schema=BudgetUpdate,
    read_schema=BudgetRead,
    prefix="/budgets",
    tags=["budgets"],
)
