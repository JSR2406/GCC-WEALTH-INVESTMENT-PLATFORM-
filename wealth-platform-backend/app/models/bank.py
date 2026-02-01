"""
Bank Model
==========

Model for bank partners (tenants) in the multi-tenant system.
Includes revenue model configuration and branding settings.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    APIStatus,
    BankStatus,
    Base,
    RevenueModel,
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.invoice import Invoice
    from app.models.revenue import RevenueCalculation
    from app.models.user import User


class Bank(Base, UUIDMixin, TimestampMixin):
    """
    Bank partner model (tenant).
    
    Each bank is a tenant with isolated data and custom branding.
    Supports multiple revenue models for platform monetization.
    """
    
    __tablename__ = "banks"
    
    # =========================================================================
    # Basic Information
    # =========================================================================
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Full bank name"
    )
    
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-friendly identifier (e.g., 'fab', 'hsbc-uae')"
    )
    
    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="ISO 3166-1 alpha-2 country code (AE or SA)"
    )
    
    # =========================================================================
    # Revenue Model Configuration
    # =========================================================================
    
    revenue_model: Mapped[RevenueModel] = mapped_column(
        Enum(RevenueModel, name="revenue_model_enum", create_constraint=True),
        nullable=False,
        default=RevenueModel.SAAS,
        comment="Revenue model type: saas, hybrid, or aum_share"
    )
    
    base_fee_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Annual subscription fee per user in USD (for SaaS/Hybrid)"
    )
    
    aum_share_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Platform's share of bank's AUM fees (1-50%)"
    )
    
    # =========================================================================
    # White-Label Branding
    # =========================================================================
    
    branding_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {
            "logo_url": "",
            "primary_color": "#1890ff",
            "secondary_color": "#52c41a",
            "font_family": "Inter",
            "app_name": ""
        },
        comment="White-label branding configuration"
    )
    
    # =========================================================================
    # API Integration
    # =========================================================================
    
    api_key_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Hashed API key for authentication"
    )
    
    api_credentials: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Encrypted bank API credentials"
    )
    
    api_base_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Base URL for bank's API"
    )
    
    api_status: Mapped[APIStatus] = mapped_column(
        Enum(APIStatus, name="api_status_enum", create_constraint=True),
        nullable=False,
        default=APIStatus.INACTIVE,
        comment="API integration status"
    )
    
    # =========================================================================
    # Platform Features
    # =========================================================================
    
    analytics_access: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether bank has access to analytics dashboard"
    )
    
    data_sharing_agreement: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Data sharing agreement configuration"
    )
    
    # =========================================================================
    # Status & Lifecycle
    # =========================================================================
    
    status: Mapped[BankStatus] = mapped_column(
        Enum(BankStatus, name="bank_status_enum", create_constraint=True),
        nullable=False,
        default=BankStatus.PENDING,
        index=True,
        comment="Bank onboarding status"
    )
    
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Timestamp when bank was fully onboarded"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    admins: Mapped[list["BankAdmin"]] = relationship(
        "BankAdmin",
        back_populates="bank",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="bank",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    revenue_calculations: Mapped[list["RevenueCalculation"]] = relationship(
        "RevenueCalculation",
        back_populates="bank",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="bank",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique constraint on slug
        UniqueConstraint("slug", name="uq_banks_slug"),
        
        # Index for common queries
        Index("idx_banks_country", "country"),
        Index("idx_banks_status", "status"),
        Index("idx_banks_revenue_model", "revenue_model"),
        
        # Check constraints for revenue model validation
        CheckConstraint(
            "(revenue_model = 'saas' AND base_fee_usd IS NOT NULL AND base_fee_usd >= 10) OR "
            "(revenue_model = 'hybrid' AND base_fee_usd IS NOT NULL AND aum_share_percentage IS NOT NULL) OR "
            "(revenue_model = 'aum_share' AND aum_share_percentage IS NOT NULL)",
            name="ck_banks_revenue_model_config"
        ),
        
        CheckConstraint(
            "aum_share_percentage IS NULL OR (aum_share_percentage >= 1 AND aum_share_percentage <= 50)",
            name="ck_banks_aum_share_range"
        ),
        
        CheckConstraint(
            "country IN ('AE', 'SA')",
            name="ck_banks_country"
        ),
        
        {"comment": "Bank partners (tenants) table"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def is_active(self) -> bool:
        """Check if bank is active."""
        return self.status == BankStatus.ACTIVE
    
    @property
    def is_api_connected(self) -> bool:
        """Check if bank API is connected."""
        return self.api_status == APIStatus.ACTIVE
    
    @property
    def app_name(self) -> str:
        """Get white-label app name."""
        return self.branding_config.get("app_name") or f"{self.name} Wealth"
    
    @property
    def primary_color(self) -> str:
        """Get primary brand color."""
        return self.branding_config.get("primary_color", "#1890ff")


class BankAdmin(Base, UUIDMixin, TimestampMixin):
    """
    Bank administrator model.
    
    Admins who manage the bank's platform configuration.
    Separate from end-users who use the wealth management features.
    """
    
    __tablename__ = "bank_admins"
    
    # =========================================================================
    # Foreign Keys
    # =========================================================================
    
    bank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Associated bank"
    )
    
    # =========================================================================
    # Admin Information
    # =========================================================================
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Admin email address"
    )
    
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Admin full name"
    )
    
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Hashed password"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Phone number"
    )
    
    # =========================================================================
    # Role & Permissions
    # =========================================================================
    
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="bank_admin",
        comment="Admin role (bank_admin, bank_super_admin)"
    )
    
    permissions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: ["view_users", "view_analytics", "edit_branding"],
        comment="List of granted permissions"
    )
    
    # =========================================================================
    # Status
    # =========================================================================
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether admin account is active"
    )
    
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether email is verified"
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Last login timestamp"
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    bank: Mapped["Bank"] = relationship(
        "Bank",
        back_populates="admins",
        foreign_keys=[bank_id]
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique email per bank
        UniqueConstraint("bank_id", "email", name="uq_bank_admins_bank_email"),
        
        Index("idx_bank_admins_bank_id", "bank_id"),
        Index("idx_bank_admins_email", "email"),
        
        {"comment": "Bank administrator accounts"}
    )
