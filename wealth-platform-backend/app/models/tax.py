"""
Tax Report Model
================

Tax compliance reporting for users.
Supports FATCA, CRS, and Zakat calculations.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TaxReportType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.user import User


class TaxReport(Base, UUIDMixin, TimestampMixin):
    """
    Tax compliance report for users.
    
    Generates FATCA, CRS, and Zakat reports based on
    user's tax residency and investments.
    """
    
    __tablename__ = "tax_reports"
    
    # =========================================================================
    # Foreign Keys
    # =========================================================================
    
    bank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("banks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owning bank (tenant)"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Report owner"
    )
    
    # =========================================================================
    # Report Details
    # =========================================================================
    
    report_type: Mapped[TaxReportType] = mapped_column(
        Enum(TaxReportType, name="tax_report_type_enum", create_constraint=True),
        nullable=False,
        comment="Type of tax report"
    )
    
    tax_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tax year for the report"
    )
    
    reporting_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Country for tax reporting"
    )
    
    # =========================================================================
    # Financial Summary
    # =========================================================================
    
    total_income: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Total income for tax year (USD)"
    )
    
    total_gains: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Total capital gains (USD)"
    )
    
    total_dividends: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Total dividend income (USD)"
    )
    
    total_interest: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Total interest income (USD)"
    )
    
    # =========================================================================
    # Zakat-Specific Fields
    # =========================================================================
    
    nisab_threshold: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        comment="Nisab threshold at time of calculation (USD)"
    )
    
    zakatable_assets: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        comment="Total zakatable assets (USD)"
    )
    
    zakat_due: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        comment="Zakat amount due (2.5% of eligible assets)"
    )
    
    # =========================================================================
    # Report Data
    # =========================================================================
    
    report_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {},
        comment="Full report data in structured format"
    )
    
    # Example report_data for FATCA:
    # {
    #   "account_holder": {...},
    #   "accounts": [...],
    #   "aggregated_balance": 250000,
    #   "filing_type": "1099-B",
    #   "forms_required": ["1099-DIV", "1099-INT"]
    # }
    
    # =========================================================================
    # Status
    # =========================================================================
    
    is_generated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether report has been generated"
    )
    
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When report was generated"
    )
    
    is_submitted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether report has been submitted to authorities"
    )
    
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When report was submitted"
    )
    
    submission_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Submission reference/confirmation number"
    )
    
    # =========================================================================
    # Documents
    # =========================================================================
    
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="S3 URL of generated PDF report"
    )
    
    xml_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="S3 URL of XML report (for CRS/FATCA)"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes or disclaimers"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    bank: Mapped["Bank"] = relationship(
        "Bank",
        lazy="selectin"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tax_reports",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique report per user per type per year
        UniqueConstraint(
            "user_id", "report_type", "tax_year",
            name="uq_tax_reports_user_type_year"
        ),
        
        # Indexes
        Index("idx_tax_reports_bank_id", "bank_id"),
        Index("idx_tax_reports_user_id", "user_id"),
        Index("idx_tax_reports_type", "report_type"),
        Index("idx_tax_reports_year", "tax_year"),
        
        # Composite indexes
        Index("idx_tax_reports_user_year", "user_id", "tax_year"),
        Index("idx_tax_reports_bank_type", "bank_id", "report_type"),
        
        {"comment": "Tax compliance reports (FATCA, CRS, Zakat)"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def total_taxable_income(self) -> Decimal:
        """Get total taxable income."""
        return self.total_income + self.total_gains + self.total_dividends + self.total_interest
    
    @property
    def is_zakat_applicable(self) -> bool:
        """Check if Zakat is applicable."""
        if self.report_type != TaxReportType.ZAKAT:
            return False
        return (
            self.zakatable_assets is not None
            and self.nisab_threshold is not None
            and self.zakatable_assets >= self.nisab_threshold
        )
    
    @property
    def report_period(self) -> str:
        """Get report period string."""
        return f"{self.tax_year}"
    
    @property
    def is_complete(self) -> bool:
        """Check if report is complete (generated and has PDF)."""
        return self.is_generated and self.pdf_url is not None
