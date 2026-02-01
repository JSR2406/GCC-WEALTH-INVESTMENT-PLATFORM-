"""
Banks API Endpoints
===================

Bank management API including:
- Self-service registration
- Dashboard analytics
- Branding configuration
- User management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AuthenticatedUser,
    BankAdmin,
    Database,
    Pagination,
    PlatformAdmin,
    RequiredTenant,
    verify_bank_access,
)
from app.core.security import generate_api_key, hash_password
from app.models.bank import Bank, BankAdmin as BankAdminModel
from app.models.revenue import RevenueCalculation
from app.models.user import User
from app.schemas.bank import (
    BankAPIConfig,
    BankAdminCreate,
    BankCreate,
    BankDashboard,
    BankRegistrationResponse,
    BankResponse,
    BankUpdate,
    BrandingConfig,
    DashboardMetrics,
    RevenueBreakdown,
    TopUser,
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.user import UserSummary

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Bank Registration (Public)
# =============================================================================

@router.post(
    "/register",
    response_model=BankRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new bank partner",
    description="""
    Self-service registration for bank partners.
    
    Creates a new bank account with:
    - Revenue model configuration
    - White-label branding
    - Initial admin account
    - API key for integrations
    
    The API key is shown only once - store it securely.
    """
)
async def register_bank(
    bank_data: BankCreate,
    admin_data: BankAdminCreate,
    db: Database
):
    """Register a new bank partner."""
    
    # Check if slug is taken
    existing = await db.execute(
        select(Bank).where(Bank.slug == bank_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "BANK_SLUG_TAKEN",
                "message": f"Bank slug '{bank_data.slug}' is already taken"
            }
        )
    
    # Generate API key
    api_key, api_key_hash = generate_api_key(prefix="pk")
    
    # Create bank
    bank = Bank(
        name=bank_data.name,
        slug=bank_data.slug,
        country=bank_data.country,
        revenue_model=bank_data.revenue_model,
        base_fee_usd=bank_data.base_fee_usd,
        aum_share_percentage=bank_data.aum_share_percentage,
        branding_config=bank_data.branding.model_dump() if bank_data.branding else {},
        api_key_hash=api_key_hash,
    )
    
    db.add(bank)
    await db.flush()  # Get bank.id
    
    # Create admin
    admin = BankAdminModel(
        bank_id=bank.id,
        email=admin_data.email,
        full_name=admin_data.full_name,
        phone=admin_data.phone,
        password_hash=hash_password(admin_data.password),
        role="bank_super_admin",
        permissions=["admin", "view_users", "edit_users", "view_analytics", "edit_branding", "manage_api"],
    )
    
    db.add(admin)
    await db.commit()
    
    logger.info(f"New bank registered: {bank.slug} (id={bank.id})")
    
    # TODO: Send verification email to admin
    
    return BankRegistrationResponse(
        bank_id=bank.id,
        slug=bank.slug,
        status=bank.status,
        api_key=api_key,
    )


# =============================================================================
# Get Bank Details
# =============================================================================

@router.get(
    "/{bank_id}",
    response_model=BankResponse,
    summary="Get bank details",
    description="Get details of a specific bank (admin access required)"
)
async def get_bank(
    bank_id: UUID,
    user: AuthenticatedUser,
    db: Database
):
    """Get bank details."""
    await verify_bank_access(bank_id, user)
    
    result = await db.execute(
        select(Bank).where(Bank.id == bank_id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BANK_NOT_FOUND", "message": "Bank not found"}
        )
    
    return BankResponse.model_validate(bank)


# =============================================================================
# Bank Dashboard
# =============================================================================

@router.get(
    "/{bank_id}/dashboard",
    response_model=BankDashboard,
    summary="Get bank analytics dashboard",
    description="""
    Retrieve bank's analytics dashboard with:
    - Active user count
    - Total AUM
    - Revenue metrics
    - Growth percentages
    - Top users (anonymized)
    """
)
async def get_dashboard(
    bank_id: UUID,
    period: str = Query("current_month", regex="^(current_month|last_month|ytd)$"),
    user: AuthenticatedUser = Depends(),
    db: Database = Depends()
):
    """Get bank analytics dashboard."""
    await verify_bank_access(bank_id, user)
    
    # Get current date info
    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year
    
    # Determine period
    if period == "current_month":
        start_month, start_year = current_month, current_year
        end_month, end_year = current_month, current_year
        period_str = f"{current_year}-{current_month:02d}"
    elif period == "last_month":
        if current_month == 1:
            start_month, start_year = 12, current_year - 1
        else:
            start_month, start_year = current_month - 1, current_year
        end_month, end_year = start_month, start_year
        period_str = f"{start_year}-{start_month:02d}"
    else:  # ytd
        start_month, start_year = 1, current_year
        end_month, end_year = current_month, current_year
        period_str = f"{current_year}-YTD"
    
    # Get active users count
    active_users_result = await db.execute(
        select(func.count(User.id))
        .where(User.bank_id == bank_id)
        .where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0
    
    # Get revenue data
    revenue_query = (
        select(
            func.sum(RevenueCalculation.total_revenue).label("total"),
            func.sum(RevenueCalculation.subscription_fee).label("subscription"),
            func.sum(RevenueCalculation.aum_revenue_share).label("aum_share"),
            func.sum(RevenueCalculation.user_aum_snapshot).label("total_aum")
        )
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year >= start_year)
        .where(RevenueCalculation.calculation_month >= start_month)
    )
    
    revenue_result = await db.execute(revenue_query)
    revenue_row = revenue_result.one()
    
    total_revenue = float(revenue_row.total or 0)
    subscription_total = float(revenue_row.subscription or 0)
    aum_share_total = float(revenue_row.aum_share or 0)
    total_aum = float(revenue_row.total_aum or 0)
    
    # Calculate YTD revenue
    ytd_query = (
        select(func.sum(RevenueCalculation.total_revenue))
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == current_year)
    )
    ytd_result = await db.execute(ytd_query)
    revenue_ytd = float(ytd_result.scalar() or 0)
    
    # Get top users (anonymized)
    top_users_query = (
        select(
            User.full_name,
            func.sum(RevenueCalculation.user_aum_snapshot).label("aum"),
            func.sum(RevenueCalculation.total_revenue).label("revenue")
        )
        .join(User, RevenueCalculation.user_id == User.id)
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == current_year)
        .where(RevenueCalculation.calculation_month == current_month)
        .group_by(User.id, User.full_name)
        .order_by(func.sum(RevenueCalculation.user_aum_snapshot).desc())
        .limit(10)
    )
    
    top_users_result = await db.execute(top_users_query)
    top_users = []
    for row in top_users_result:
        # Anonymize name to initials
        name_parts = row.full_name.split()
        initials = f"{name_parts[0][0]}.{name_parts[-1][0]}." if len(name_parts) >= 2 else f"{name_parts[0][0]}."
        top_users.append(TopUser(
            initials=initials,
            aum=row.aum or 0,
            revenue_contribution=row.revenue or 0
        ))
    
    # TODO: Calculate actual growth percentages
    user_growth = 12.5  # Placeholder
    aum_growth = 8.3    # Placeholder
    
    return BankDashboard(
        period=period_str,
        metrics=DashboardMetrics(
            active_users=active_users,
            total_aum=total_aum,
            revenue_this_month=total_revenue,
            revenue_ytd=revenue_ytd
        ),
        revenue_breakdown=RevenueBreakdown(
            subscription_fees=subscription_total,
            aum_revenue_share=aum_share_total
        ),
        user_growth_percentage=user_growth,
        aum_growth_percentage=aum_growth,
        top_users=top_users
    )


# =============================================================================
# Update Branding
# =============================================================================

@router.put(
    "/{bank_id}/branding",
    response_model=BankResponse,
    summary="Update bank branding",
    description="Update white-label branding configuration"
)
async def update_branding(
    bank_id: UUID,
    branding: BrandingConfig,
    user: BankAdmin,
    db: Database
):
    """Update bank's white-label branding."""
    await verify_bank_access(bank_id, user)
    
    result = await db.execute(
        select(Bank).where(Bank.id == bank_id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BANK_NOT_FOUND", "message": "Bank not found"}
        )
    
    # Update branding
    bank.branding_config = branding.model_dump()
    await db.commit()
    await db.refresh(bank)
    
    logger.info(f"Bank branding updated: {bank.slug}")
    
    # TODO: Invalidate cache, trigger webhook
    
    return BankResponse.model_validate(bank)


# =============================================================================
# Get Bank Users
# =============================================================================

@router.get(
    "/{bank_id}/users",
    response_model=PaginatedResponse[UserSummary],
    summary="List bank users",
    description="Get paginated list of bank's users"
)
async def list_bank_users(
    bank_id: UUID,
    pagination: Pagination,
    search: Optional[str] = Query(None, description="Search by name or email"),
    kyc_status: Optional[str] = Query(None, description="Filter by KYC status"),
    user: BankAdmin = Depends(),
    db: Database = Depends()
):
    """List users for a bank."""
    await verify_bank_access(bank_id, user)
    
    # Build query
    query = select(User).where(User.bank_id == bank_id)
    
    if search:
        query = query.where(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if kyc_status:
        query = query.where(User.kyc_status == kyc_status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0
    
    # Paginate
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
    
    return PaginatedResponse(
        data=[UserSummary.model_validate(u) for u in users],
        pagination=PaginationMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    )


# =============================================================================
# Configure API
# =============================================================================

@router.post(
    "/{bank_id}/api-config",
    response_model=SuccessResponse,
    summary="Configure bank API integration",
    description="Set up connection to bank's API"
)
async def configure_api(
    bank_id: UUID,
    config: BankAPIConfig,
    user: BankAdmin,
    db: Database
):
    """Configure bank API integration."""
    await verify_bank_access(bank_id, user)
    
    result = await db.execute(
        select(Bank).where(Bank.id == bank_id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BANK_NOT_FOUND", "message": "Bank not found"}
        )
    
    # Store encrypted credentials
    from app.core.security import encrypt_pii
    
    bank.api_base_url = config.api_base_url
    bank.api_credentials = {
        "client_id": config.client_id,
        "client_secret": encrypt_pii(config.client_secret) if config.client_secret else None,
        "webhook_secret": encrypt_pii(config.webhook_secret) if config.webhook_secret else None,
    }
    bank.api_status = "testing"
    
    await db.commit()
    
    logger.info(f"Bank API configured: {bank.slug}")
    
    return SuccessResponse(
        message="API configuration saved. Status set to 'testing'."
    )


# =============================================================================
# List All Banks (Platform Admin)
# =============================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BankResponse],
    summary="List all banks",
    description="List all banks (platform admin only)"
)
async def list_banks(
    pagination: Pagination,
    status: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    user: PlatformAdmin = Depends(),
    db: Database = Depends()
):
    """List all banks (platform admin only)."""
    
    query = select(Bank)
    
    if status:
        query = query.where(Bank.status == status)
    if country:
        query = query.where(Bank.country == country.upper())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0
    
    # Paginate
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    banks = result.scalars().all()
    
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
    
    return PaginatedResponse(
        data=[BankResponse.model_validate(b) for b in banks],
        pagination=PaginationMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    )
