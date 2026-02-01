"""
Invoice Model
=============

Monthly invoices for bank partners based on revenue calculations.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, InvoiceStatus, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.revenue import RevenueCalculation


class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Invoice for bank partners.
    
    Generated monthly based on revenue calculations.
    Includes PDF storage and payment tracking.
    """
    
    __tablename__ = "invoices"
    
    # =========================================================================
    # Foreign Keys
    # =========================================================================
    
    bank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("banks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bank being invoiced"
    )
    
    # =========================================================================
    # Invoice Identification
    # =========================================================================
    
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique invoice number (e.g., INV-2026-02-001)"
    )
    
    # =========================================================================
    # Period
    # =========================================================================
    
    billing_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Billing month (1-12)"
    )
    
    billing_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Billing year"
    )
    
    # =========================================================================
    # Invoice Details
    # =========================================================================
    
    total_users: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of active users in billing period"
    )
    
    total_aum: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Total AUM for billing period (USD)"
    )
    
    # =========================================================================
    # Revenue Breakdown
    # =========================================================================
    
    subscription_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Total subscription fees (USD)"
    )
    
    aum_share_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Total AUM revenue share (USD)"
    )
    
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Subtotal before tax (USD)"
    )
    
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Tax amount (typically 0 for UAE/SA)"
    )
    
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Total invoice amount (USD)"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="Invoice currency"
    )
    
    # =========================================================================
    # Status & Payment
    # =========================================================================
    
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status_enum", create_constraint=True),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        index=True,
        comment="Invoice status"
    )
    
    due_date: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Payment due date"
    )
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When payment was received"
    )
    
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Payment method used"
    )
    
    payment_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Payment reference/transaction ID"
    )
    
    # =========================================================================
    # Stripe Integration
    # =========================================================================
    
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Stripe invoice ID"
    )
    
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Stripe payment intent ID"
    )
    
    # =========================================================================
    # Documents
    # =========================================================================
    
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="S3 URL of PDF invoice"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes"
    )
    
    # =========================================================================
    # Line Items (for detailed breakdown)
    # =========================================================================
    
    line_items: Mapped[Optional[list[dict]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: [],
        comment="Detailed line items"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    bank: Mapped["Bank"] = relationship(
        "Bank",
        back_populates="invoices",
        lazy="selectin"
    )
    
    revenue_calculations: Mapped[list["RevenueCalculation"]] = relationship(
        "RevenueCalculation",
        back_populates="invoice",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique invoice per bank per period
        Index(
            "idx_invoices_bank_period",
            "bank_id", "billing_year", "billing_month",
            unique=True
        ),
        
        # Indexes
        Index("idx_invoices_bank_id", "bank_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_due_date", "due_date"),
        
        # Check constraints
        CheckConstraint(
            "billing_month >= 1 AND billing_month <= 12",
            name="ck_invoices_month_range"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_invoices_total_positive"
        ),
        
        {"comment": "Monthly invoices for bank partners"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def period(self) -> str:
        """Get period as YYYY-MM string."""
        return f"{self.billing_year}-{self.billing_month:02d}"
    
    @property
    def is_paid(self) -> bool:
        """Check if invoice is paid."""
        return self.status == InvoiceStatus.PAID
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def amount_due(self) -> Decimal:
        """Get amount due (0 if paid)."""
        if self.is_paid:
            return Decimal(0)
        return self.total_amount
