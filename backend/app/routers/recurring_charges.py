from app.models.recurring_charge import RecurringCharge
from app.routers._crud import build_crud_router
from app.schemas.recurring_charge import (
    RecurringChargeCreate,
    RecurringChargeRead,
    RecurringChargeUpdate,
)

router = build_crud_router(
    model=RecurringCharge,
    create_schema=RecurringChargeCreate,
    update_schema=RecurringChargeUpdate,
    read_schema=RecurringChargeRead,
    prefix="/recurring-charges",
    tags=["recurring-charges"],
)
