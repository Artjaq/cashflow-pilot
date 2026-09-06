from app.models.category import Category
from app.routers._crud import build_crud_router
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = build_crud_router(
    model=Category,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    read_schema=CategoryRead,
    prefix="/categories",
    tags=["categories"],
)
