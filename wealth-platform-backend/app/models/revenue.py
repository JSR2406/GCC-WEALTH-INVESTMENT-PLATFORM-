"""
Revenue Calculation Model
========================

Tracks platform revenue from each bank user.
Supports SaaS, Hybrid, and AUM Share revenue models.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.invoice import Invoice
    from app.models.user import User


class RevenueCalculation(Base, UUIDMixin, TimestampMixin):
    """
    Revenue calculation per user per month.
    
    Stores the breakdown of revenue generated from each user
    based on their bank's revenue model configuration.
    """
    
    __tablename__ = "revenue_calculations"
    
    # =========================================================================
    # Foreign Keys
    # =========================================================================
    
    bank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("banks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bank generating the revenue"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User generating the revenue"
    )
    
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Associated invoice (when invoiced)"
    )
    
    # =========================================================================
    # Period
    # =========================================================================
    
    calculation_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Month of calculation (1-12)"
    )
    
    calculation_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Year of calculation"
    )
    
    # =========================================================================
    # AUM Snapshot
    # =========================================================================
    
    user_aum_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="User's total AUM at end of month (USD)"
    )
    
    # =========================================================================
    # Revenue Breakdown
    # =========================================================================
    
    subscription_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Monthly subscription fee portion (USD)"
    )
    
    aum_revenue_share: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="AUM-based revenue share portion (USD)"
    )
    
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total revenue for this user this month (USD)"
    )
    
    # =========================================================================
    # Pro-rating
    # =========================================================================
    
    days_active: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        comment="Days user was active in the month"
    )
    
    is_prorated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether fees were pro-rated (mid-month activation)"
    )
    
    # =========================================================================
    # Invoice Status
    # =========================================================================
    
    is_invoiced: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether this calculation is included in an invoice"
    )
    
    invoiced_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When the calculation was invoiced"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    bank: Mapped["Bank"] = relationship(
        "Bank",
        back_populates="revenue_calculations",
        lazy="selectin"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="revenue_calculations",
        lazy="selectin"
    )
    
    invoice: Mapped[Optional["Invoice"]] = relationship(
        "Invoice",
        back_populates="revenue_calculations",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Each user can only have one calculation per period
        UniqueConstraint(
            "user_id", "calculation_month", "calculation_year",
            name="uq_revenue_user_period"
        ),
        
        # Indexes
        Index("idx_revenue_bank_id", "bank_id"),
        Index("idx_revenue_user_id", "user_id"),
        Index("idx_revenue_invoice_id", "invoice_id"),
        Index("idx_revenue_invoiced", "is_invoiced"),
        
        # Composite indexes for period queries
        Index(
            "idx_revenue_bank_period",
            "bank_id", "calculation_year", "calculation_month"
        ),
        Index(
            "idx_revenue_year_month",
            "calculation_year", "calculation_month"
        ),
        
        # Check constraints
        CheckConstraint(
            "calculation_month >= 1 AND calculation_month <= 12",
            name="ck_revenue_month_range"
        ),
        CheckConstraint(
            "total_revenue >= 0",
            name="ck_revenue_total_positive"
        ),
        CheckConstraint(
            "subscription_fee >= 0",
            name="ck_revenue_subscription_positive"
        ),
        CheckConstraint(
            "aum_revenue_share >= 0",
            name="ck_revenue_aum_share_positive"
        ),
        
        {"comment": "Monthly revenue calculations per user"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def period(self) -> str:
        """Get period as YYYY-MM string."""
        return f"{self.calculation_year}-{self.calculation_month:02d}"
    
    @property
    def subscription_percentage(self) -> float:
        """Get subscription fee as percentage of total."""
        if self.total_revenue == 0:
            return 0
        return float(self.subscription_fee / self.total_revenue * 100)
    
    @property
    def aum_share_percentage(self) -> float:
        """Get AUM share as percentage of total."""
        if self.total_revenue == 0:
            return 0
        return float(self.aum_revenue_share / self.total_revenue * 100)
