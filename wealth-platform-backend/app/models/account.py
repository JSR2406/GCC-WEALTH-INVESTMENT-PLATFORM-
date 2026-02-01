"""
User Account Model
==================

Bank accounts linked to users (savings, checking, investment).
Stores balance snapshots and account metadata.
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
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AccountType,
    Base,
    TenantMixin,
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.user import User


class UserAccount(Base, UUIDMixin, TimestampMixin):
    """
    User's bank account model.
    
    Represents accounts linked from the bank's system.
    Used for AUM calculations and portfolio tracking.
    """
    
    __tablename__ = "user_accounts"
    
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
        comment="Account owner"
    )
    
    # =========================================================================
    # Account Information
    # =========================================================================
    
    external_account_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Account ID in bank's system"
    )
    
    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type_enum", create_constraint=True),
        nullable=False,
        comment="Type of account"
    )
    
    account_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Account name/label"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="Account currency (ISO 4217)"
    )
    
    # =========================================================================
    # Balance Information
    # =========================================================================
    
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Current account balance"
    )
    
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Available balance (may differ from current)"
    )
    
    balance_usd: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Balance converted to USD"
    )
    
    balance_updated_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When balance was last synced"
    )
    
    # =========================================================================
    # Investment Holdings (for investment accounts)
    # =========================================================================
    
    holdings: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: [],
        comment="Investment holdings (for investment accounts)"
    )
    
    # Example holdings structure:
    # [
    #   {
    #     "ticker": "AAPL",
    #     "name": "Apple Inc.",
    #     "quantity": 100,
    #     "avg_purchase_price": 150.00,
    #     "current_price": 175.50,
    #     "total_value": 17550.00,
    #     "currency": "USD"
    #   }
    # ]
    
    # =========================================================================
    # Account Metadata
    # =========================================================================
    
    iban: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="IBAN (for savings/checking)"
    )
    
    opened_date: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When account was opened"
    )
    
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the primary account"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether account is active for sync"
    )
    
    # =========================================================================
    # Sync Status
    # =========================================================================
    
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Last successful sync timestamp"
    )
    
    sync_error: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Last sync error message"
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
        back_populates="accounts",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Unique external account ID per bank
        UniqueConstraint(
            "bank_id", "external_account_id",
            name="uq_user_accounts_bank_external_id"
        ),
        
        # Indexes
        Index("idx_user_accounts_bank_id", "bank_id"),
        Index("idx_user_accounts_user_id", "user_id"),
        Index("idx_user_accounts_type", "account_type"),
        Index("idx_user_accounts_active", "is_active"),
        
        # Composite indexes
        Index("idx_user_accounts_user_type", "user_id", "account_type"),
        
        {"comment": "User bank accounts for AUM tracking"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def total_value(self) -> Decimal:
        """Get total value in account currency."""
        return self.current_balance
    
    @property
    def total_value_usd(self) -> Decimal:
        """Get total value in USD."""
        return self.balance_usd
    
    @property
    def is_investment(self) -> bool:
        """Check if this is an investment account."""
        return self.account_type == AccountType.INVESTMENT
    
    @property
    def holdings_count(self) -> int:
        """Get number of holdings."""
        return len(self.holdings) if self.holdings else 0
    
    def get_holding(self, ticker: str) -> Optional[dict]:
        """Get a specific holding by ticker."""
        if not self.holdings:
            return None
        for holding in self.holdings:
            if holding.get("ticker") == ticker:
                return holding
        return None
