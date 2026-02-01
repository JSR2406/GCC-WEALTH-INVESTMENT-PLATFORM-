"""
API Version 1 Router
====================

Aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.banks import router as banks_router
from app.api.v1.portfolios import router as portfolios_router
from app.api.v1.revenue import router as revenue_router
from app.api.v1.users import router as users_router
from app.api.v1.fees import router as fees_router

router = APIRouter()

# Bank Management
router.include_router(
    banks_router,
    prefix="/banks",
    tags=["Banks"]
)

# User Management
router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

# Portfolio & Goals
router.include_router(
    portfolios_router,
    prefix="/portfolios",
    tags=["Portfolios"]
)

# Revenue & Invoices
router.include_router(
    revenue_router,
    prefix="/revenue",
    tags=["Revenue"]
)

# Service Fees
router.include_router(
    fees_router,
    prefix="/fees",
    tags=["Service Fees"]
)
