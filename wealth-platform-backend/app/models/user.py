"""
User Model
==========

End-user model for bank customers using the wealth management platform.
Includes KYC status, tax residency, and subscription information.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    KYCStatus,
    SubscriptionTier,
    TenantMixin,
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.account import UserAccount
    from app.models.bank import Bank
    from app.models.goal import InvestmentGoal
    from app.models.revenue import RevenueCalculation
    from app.models.tax import TaxReport


class User(Base, UUIDMixin, TimestampMixin):
    """
    End-user model (bank customers).
    
    Users belong to a specific bank (tenant) and use the
    white-labeled wealth management features.
    """
    
    __tablename__ = "users"
    
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
    
    # =========================================================================
    # Basic Information
    # =========================================================================
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User email address"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Phone number with country code"
    )
    
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User's full legal name"
    )
    
    nationality: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="ISO 3166-1 alpha-2 nationality code"
    )
    
    residency_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Current country of residence (AE or SA)"
    )
    
    # =========================================================================
    # KYC Information
    # =========================================================================
    
    kyc_status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus, name="kyc_status_enum", create_constraint=True),
        nullable=False,
        default=KYCStatus.PENDING,
        index=True,
        comment="KYC verification status"
    )
    
    kyc_documents: Mapped[Optional[list[dict]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: [],
        comment="Array of KYC document URLs with metadata"
    )
    
    kyc_verified_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When KYC was verified"
    )
    
    # =========================================================================
    # Identity Documents (Encrypted)
    # =========================================================================
    
    emirates_id_encrypted: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Encrypted Emirates ID number"
    )
    
    iqama_number_encrypted: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Encrypted Saudi Iqama number"
    )
    
    # =========================================================================
    # Tax Information
    # =========================================================================
    
    tax_residency_countries: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: [],
        comment="Countries of tax residency"
    )
    
    us_person: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether user is a US person (for FATCA)"
    )
    
    tin_numbers_encrypted: Mapped[Optional[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Encrypted tax identification numbers by country"
    )
    
    # =========================================================================
    # Subscription
    # =========================================================================
    
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, name="subscription_tier_enum", create_constraint=True),
        nullable=False,
        default=SubscriptionTier.BASIC,
        comment="User subscription tier"
    )
    
    # =========================================================================
    # Authentication
    # =========================================================================
    
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Hashed password (if direct login enabled)"
    )
    
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="External bank customer ID"
    )
    
    # =========================================================================
    # Status & Lifecycle
    # =========================================================================
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether user account is active"
    )
    
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When user completed onboarding"
    )
    
    last_active: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        index=True,
        comment="Last activity timestamp"
    )
    
    # =========================================================================
    # Risk Profile
    # =========================================================================
    
    risk_profile: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="User's investment risk profile assessment"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    bank: Mapped["Bank"] = relationship(
        "Bank",
        back_populates="users",
        lazy="selectin"
    )
    
    accounts: Mapped[list["UserAccount"]] = relationship(
        "UserAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    goals: Mapped[list["InvestmentGoal"]] = relationship(
        "InvestmentGoal",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    revenue_calculations: Mapped[list["RevenueCalculation"]] = relationship(
        "RevenueCalculation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    tax_reports: Mapped[list["TaxReport"]] = relationship(
        "TaxReport",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique email per bank
        UniqueConstraint("bank_id", "email", name="uq_users_bank_email"),
        
        # Indexes
        Index("idx_users_bank_id", "bank_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_kyc_status", "kyc_status"),
        Index("idx_users_nationality", "nationality"),
        Index("idx_users_residency", "residency_country"),
        Index("idx_users_last_active", "last_active"),
        
        # Composite indexes for common queries
        Index("idx_users_bank_active", "bank_id", "is_active"),
        Index("idx_users_bank_kyc", "bank_id", "kyc_status"),
        
        # Check constraints
        CheckConstraint(
            "residency_country IN ('AE', 'SA')",
            name="ck_users_residency_country"
        ),
        
        {"comment": "End-user accounts (bank customers)"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def is_kyc_verified(self) -> bool:
        """Check if KYC is verified."""
        return self.kyc_status == KYCStatus.VERIFIED
    
    @property
    def is_us_reportable(self) -> bool:
        """Check if user requires FATCA reporting."""
        return self.us_person or "US" in self.tax_residency_countries
    
    @property
    def display_name(self) -> str:
        """Get display name (first name only for privacy)."""
        parts = self.full_name.split()
        return parts[0] if parts else "User"
    
    @property
    def initials(self) -> str:
        """Get user initials for anonymization."""
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}.{parts[-1][0]}."
        return parts[0][0] + "." if parts else "U."
    
    def has_residency(self, country: str) -> bool:
        """Check if user has residency in country."""
        return self.residency_country == country
