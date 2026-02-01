"""
Revenue Schemas
===============

Pydantic schemas for revenue calculation API.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Revenue Calculation Request/Response
# =============================================================================

class RevenueCalculationRequest(BaseModel):
    """Request to trigger revenue calculation."""
    
    bank_id: Optional[UUID] = Field(
        None,
        description="Specific bank ID (all banks if null)"
    )
    month: int = Field(..., ge=1, le=12, description="Month to calculate (1-12)")
    year: int = Field(..., ge=2020, le=2100, description="Year to calculate")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_id": None,
                "month": 1,
                "year": 2026
            }
        }
    )


class RevenueCalculationResponse(BaseModel):
    """Response after revenue calculation."""
    
    calculations_created: int = Field(
        ..., ge=0, description="Number of calculations created"
    )
    total_revenue: Decimal = Field(
        ..., ge=0, description="Total revenue calculated"
    )
    invoice_id: Optional[UUID] = Field(
        None, description="Generated invoice ID"
    )
    invoice_pdf_url: Optional[str] = Field(
        None, description="URL to invoice PDF"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "calculations_created": 1250,
                "total_revenue": 15625.00,
                "invoice_id": "550e8400-e29b-41d4-a716-446655440000",
                "invoice_pdf_url": "https://s3.amazonaws.com/invoices/INV-2026-01-001.pdf"
            }
        }
    )


# =============================================================================
# Revenue History
# =============================================================================

class RevenueHistoryItem(BaseModel):
    """Single period revenue history."""
    
    period: str = Field(..., description="Period (YYYY-MM)")
    total_revenue: Decimal = Field(..., ge=0)
    subscription_fees: Decimal = Field(..., ge=0)
    aum_share: Decimal = Field(..., ge=0)
    active_users: int = Field(..., ge=0)
    total_aum: Decimal = Field(..., ge=0)
    avg_aum_per_user: Decimal = Field(..., ge=0)
    growth_percentage: float = Field(..., description="Growth vs previous period")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": "2026-01",
                "total_revenue": 15000.00,
                "subscription_fees": 3000.00,
                "aum_share": 12000.00,
                "active_users": 1200,
                "total_aum": 60000000.00,
                "avg_aum_per_user": 50000.00,
                "growth_percentage": 8.5
            }
        }
    )


class RevenueHistory(BaseModel):
    """Revenue history response."""
    
    bank_id: UUID
    bank_name: str
    periods: List[RevenueHistoryItem]
    total_revenue_all_time: Decimal = Field(..., ge=0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_id": "550e8400-e29b-41d4-a716-446655440000",
                "bank_name": "First Abu Dhabi Bank",
                "periods": [],
                "total_revenue_all_time": 93750.00
            }
        }
    )


# =============================================================================
# Revenue Detail (per user)
# =============================================================================

class UserRevenueDetail(BaseModel):
    """Revenue detail for a specific user."""
    
    id: UUID
    user_id: UUID
    user_initials: str = Field(..., description="Anonymized user identifier")
    calculation_month: int
    calculation_year: int
    user_aum_snapshot: Decimal
    subscription_fee: Decimal
    aum_revenue_share: Decimal
    total_revenue: Decimal
    is_prorated: bool
    is_invoiced: bool
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Invoice
# =============================================================================

class InvoiceResponse(BaseModel):
    """Invoice response schema."""
    
    id: UUID
    invoice_number: str
    bank_id: UUID
    billing_month: int
    billing_year: int
    total_users: int
    total_aum: Decimal
    subscription_total: Decimal
    aum_share_total: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    status: str
    due_date: datetime
    paid_at: Optional[datetime] = None
    pdf_url: Optional[str] = None
    created_at: datetime
    
    @property
    def period(self) -> str:
        return f"{self.billing_year}-{self.billing_month:02d}"
    
    model_config = ConfigDict(from_attributes=True)


class InvoiceListItem(BaseModel):
    """Compact invoice for lists."""
    
    id: UUID
    invoice_number: str
    period: str
    total_amount: Decimal
    status: str
    due_date: datetime
    paid_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Revenue Summary (for dashboard)
# =============================================================================

class RevenueSummary(BaseModel):
    """Revenue summary for dashboard."""
    
    current_month: Decimal = Field(..., ge=0)
    previous_month: Decimal = Field(..., ge=0)
    ytd: Decimal = Field(..., ge=0)
    last_year_total: Decimal = Field(..., ge=0)
    mom_growth: float = Field(..., description="Month-over-month growth %")
    yoy_growth: float = Field(..., description="Year-over-year growth %")
    projected_annual: Decimal = Field(..., ge=0, description="Projected annual revenue")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_month": 15625.00,
                "previous_month": 14500.00,
                "ytd": 31250.00,
                "last_year_total": 175000.00,
                "mom_growth": 7.76,
                "yoy_growth": 12.5,
                "projected_annual": 187500.00
            }
        }
    )
