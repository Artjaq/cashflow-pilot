from app.models.merchant import Merchant
from app.routers._crud import build_crud_router
from app.schemas.merchant import MerchantCreate, MerchantRead, MerchantUpdate

router = build_crud_router(
    model=Merchant,
    create_schema=MerchantCreate,
    update_schema=MerchantUpdate,
    read_schema=MerchantRead,
    prefix="/merchants",
    tags=["merchants"],
)
