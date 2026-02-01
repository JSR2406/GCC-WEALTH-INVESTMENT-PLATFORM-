"""
Revenue API Endpoints
=====================

Revenue calculation and invoice management.
"""

import logging
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
    verify_bank_access,
)
from app.models.bank import Bank
from app.models.invoice import Invoice
from app.models.revenue import RevenueCalculation
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.revenue import (
    InvoiceListItem,
    InvoiceResponse,
    RevenueCalculationRequest,
    RevenueCalculationResponse,
    RevenueHistory,
    RevenueHistoryItem,
    RevenueSummary,
    UserRevenueDetail,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Trigger Revenue Calculation (Platform Admin)
# =============================================================================

@router.post(
    "/calculate",
    response_model=RevenueCalculationResponse,
    summary="Trigger revenue calculation",
    description="Manually trigger revenue calculation (platform admin only)"
)
async def trigger_revenue_calculation(
    request: RevenueCalculationRequest,
    user: PlatformAdmin,
    db: Database
):
    """Trigger revenue calculation for a bank/all banks."""
    
    # This would normally call the revenue calculator service
    # For now, return a placeholder response
    
    logger.info(
        f"Revenue calculation triggered: bank={request.bank_id}, "
        f"period={request.year}-{request.month:02d}"
    )
    
    # TODO: Implement actual revenue calculation
    # from app.services.revenue_calculator import RevenueCalculator
    # calculator = RevenueCalculator()
    # result = await calculator.calculate_monthly_revenue(
    #     db, request.bank_id, request.month, request.year
    # )
    
    return RevenueCalculationResponse(
        calculations_created=0,
        total_revenue=0,
        invoice_id=None,
        invoice_pdf_url=None
    )


# =============================================================================
# Get Revenue History
# =============================================================================

@router.get(
    "/bank/{bank_id}/history",
    response_model=RevenueHistory,
    summary="Get revenue history",
    description="Get bank's revenue history with trend analysis"
)
async def get_revenue_history(
    bank_id: UUID,
    start_month: int = Query(1, ge=1, le=12),
    start_year: int = Query(2024),
    end_month: int = Query(12, ge=1, le=12),
    end_year: int = Query(2026),
    user: AuthenticatedUser = Depends(),
    db: Database = Depends()
):
    """Get bank's revenue history."""
    await verify_bank_access(bank_id, user)
    
    # Get bank
    bank_result = await db.execute(
        select(Bank).where(Bank.id == bank_id)
    )
    bank = bank_result.scalar_one_or_none()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BANK_NOT_FOUND"}
        )
    
    # Get revenue data grouped by period
    query = (
        select(
            RevenueCalculation.calculation_year,
            RevenueCalculation.calculation_month,
            func.sum(RevenueCalculation.total_revenue).label("total"),
            func.sum(RevenueCalculation.subscription_fee).label("subscription"),
            func.sum(RevenueCalculation.aum_revenue_share).label("aum_share"),
            func.sum(RevenueCalculation.user_aum_snapshot).label("total_aum"),
            func.count(RevenueCalculation.id).label("user_count")
        )
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year >= start_year)
        .where(RevenueCalculation.calculation_year <= end_year)
        .group_by(
            RevenueCalculation.calculation_year,
            RevenueCalculation.calculation_month
        )
        .order_by(
            RevenueCalculation.calculation_year,
            RevenueCalculation.calculation_month
        )
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    periods = []
    prev_revenue = 0
    total_all_time = 0
    
    for row in rows:
        total_revenue = float(row.total or 0)
        total_all_time += total_revenue
        
        growth = 0
        if prev_revenue > 0:
            growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        avg_aum = float(row.total_aum or 0) / max(row.user_count, 1)
        
        periods.append(RevenueHistoryItem(
            period=f"{row.calculation_year}-{row.calculation_month:02d}",
            total_revenue=total_revenue,
            subscription_fees=float(row.subscription or 0),
            aum_share=float(row.aum_share or 0),
            active_users=row.user_count,
            total_aum=float(row.total_aum or 0),
            avg_aum_per_user=avg_aum,
            growth_percentage=round(growth, 2)
        ))
        
        prev_revenue = total_revenue
    
    return RevenueHistory(
        bank_id=bank_id,
        bank_name=bank.name,
        periods=periods,
        total_revenue_all_time=total_all_time
    )


# =============================================================================
# Get Revenue Summary
# =============================================================================

@router.get(
    "/bank/{bank_id}/summary",
    response_model=RevenueSummary,
    summary="Get revenue summary",
    description="Get bank's revenue summary for dashboard"
)
async def get_revenue_summary(
    bank_id: UUID,
    user: AuthenticatedUser,
    db: Database
):
    """Get revenue summary."""
    await verify_bank_access(bank_id, user)
    
    from datetime import datetime
    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year
    
    # Previous month
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    
    # Current month revenue
    current_result = await db.execute(
        select(func.sum(RevenueCalculation.total_revenue))
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == current_year)
        .where(RevenueCalculation.calculation_month == current_month)
    )
    current_month_revenue = float(current_result.scalar() or 0)
    
    # Previous month revenue
    prev_result = await db.execute(
        select(func.sum(RevenueCalculation.total_revenue))
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == prev_year)
        .where(RevenueCalculation.calculation_month == prev_month)
    )
    prev_month_revenue = float(prev_result.scalar() or 0)
    
    # YTD revenue
    ytd_result = await db.execute(
        select(func.sum(RevenueCalculation.total_revenue))
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == current_year)
    )
    ytd_revenue = float(ytd_result.scalar() or 0)
    
    # Last year total
    last_year_result = await db.execute(
        select(func.sum(RevenueCalculation.total_revenue))
        .where(RevenueCalculation.bank_id == bank_id)
        .where(RevenueCalculation.calculation_year == current_year - 1)
    )
    last_year_total = float(last_year_result.scalar() or 0)
    
    # Calculate growth
    mom_growth = 0
    if prev_month_revenue > 0:
        mom_growth = ((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100
    
    yoy_growth = 0
    if last_year_total > 0:
        yoy_growth = ((ytd_revenue * 12 / current_month - last_year_total) / last_year_total) * 100
    
    # Project annual revenue
    projected = ytd_revenue * 12 / current_month if current_month > 0 else 0
    
    return RevenueSummary(
        current_month=current_month_revenue,
        previous_month=prev_month_revenue,
        ytd=ytd_revenue,
        last_year_total=last_year_total,
        mom_growth=round(mom_growth, 2),
        yoy_growth=round(yoy_growth, 2),
        projected_annual=round(projected, 2)
    )


# =============================================================================
# Get Invoices
# =============================================================================

@router.get(
    "/bank/{bank_id}/invoices",
    response_model=PaginatedResponse[InvoiceListItem],
    summary="List bank invoices",
    description="Get paginated list of bank's invoices"
)
async def list_invoices(
    bank_id: UUID,
    pagination: Pagination,
    status_filter: Optional[str] = Query(None, alias="status"),
    user: BankAdmin = Depends(),
    db: Database = Depends()
):
    """List invoices for a bank."""
    await verify_bank_access(bank_id, user)
    
    query = select(Invoice).where(Invoice.bank_id == bank_id)
    
    if status_filter:
        query = query.where(Invoice.status == status_filter)
    
    query = query.order_by(Invoice.billing_year.desc(), Invoice.billing_month.desc())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0
    
    # Paginate
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
    
    items = []
    for inv in invoices:
        items.append(InvoiceListItem(
            id=inv.id,
            invoice_number=inv.invoice_number,
            period=f"{inv.billing_year}-{inv.billing_month:02d}",
            total_amount=inv.total_amount,
            status=inv.status.value,
            due_date=inv.due_date,
            paid_at=inv.paid_at
        ))
    
    return PaginatedResponse(
        data=items,
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
# Get Invoice Details
# =============================================================================

@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get invoice details",
    description="Get detailed invoice information"
)
async def get_invoice(
    invoice_id: UUID,
    user: AuthenticatedUser,
    db: Database
):
    """Get invoice details."""
    
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INVOICE_NOT_FOUND"}
        )
    
    await verify_bank_access(invoice.bank_id, user)
    
    return InvoiceResponse.model_validate(invoice)
