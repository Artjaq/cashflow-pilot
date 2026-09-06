from app.models.loan import Loan, LoanRepayment
from app.routers._crud import build_crud_router
from app.schemas.loan import (
    LoanCreate,
    LoanRead,
    LoanRepaymentCreate,
    LoanRepaymentRead,
    LoanRepaymentUpdate,
    LoanUpdate,
)

router = build_crud_router(
    model=Loan,
    create_schema=LoanCreate,
    update_schema=LoanUpdate,
    read_schema=LoanRead,
    prefix="/loans",
    tags=["loans"],
)

repayments_router = build_crud_router(
    model=LoanRepayment,
    create_schema=LoanRepaymentCreate,
    update_schema=LoanRepaymentUpdate,
    read_schema=LoanRepaymentRead,
    prefix="/loan-repayments",
    tags=["loans"],
)
