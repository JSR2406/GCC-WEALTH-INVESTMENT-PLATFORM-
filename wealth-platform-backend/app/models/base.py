"""
Base Model Classes
==================

Provides mixins and base classes for all SQLAlchemy models:
- UUIDMixin: UUID primary key
- TimestampMixin: created_at, updated_at columns
- SoftDeleteMixin: Soft delete with deleted_at
- TenantMixin: Multi-tenant isolation with bank_id
"""

import uuid
import enum
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.
    
    All models should inherit from this class.
    """
    pass


class UUIDMixin:
    """
    Mixin providing UUID primary key.
    
    Uses PostgreSQL UUID type with automatic generation.
    """
    
    @declared_attr
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            index=True,
        )


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamps.
    
    - created_at: Set automatically on insert
    - updated_at: Updated automatically on update
    """
    
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    
    @declared_attr
    def updated_at(cls) -> Mapped[Optional[datetime]]:
        return mapped_column(
            DateTime(timezone=True),
            default=None,
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=True,
        )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    
    Records are marked as deleted instead of being removed.
    """
    
    @declared_attr
    def deleted_at(cls) -> Mapped[Optional[datetime]]:
        return mapped_column(
            DateTime(timezone=True),
            default=None,
            nullable=True,
            index=True,
        )
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """Restore soft deleted record."""
        self.deleted_at = None


class TenantMixin:
    """
    Mixin for multi-tenant isolation.
    
    All tenant-scoped models should include this mixin.
    Provides bank_id foreign key with index for query optimization.
    """
    
    @declared_attr
    def bank_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("banks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )


# =============================================================================
# Enum Types
# =============================================================================

class BankStatus(str, enum.Enum):
    """Bank account status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class RevenueModel(str, enum.Enum):
    """Revenue model types."""
    SAAS = "saas"
    HYBRID = "hybrid"
    AUM_SHARE = "aum_share"


class APIStatus(str, enum.Enum):
    """Bank API integration status."""
    INACTIVE = "inactive"
    TESTING = "testing"
    ACTIVE = "active"


class KYCStatus(str, enum.Enum):
    """User KYC verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class SubscriptionTier(str, enum.Enum):
    """User subscription tier."""
    BASIC = "basic"
    PREMIUM = "premium"


class AccountType(str, enum.Enum):
    """Bank account types."""
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"


class GoalType(str, enum.Enum):
    """Investment goal types."""
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME = "home"
    TRAVEL = "travel"
    EMERGENCY = "emergency"
    CUSTOM = "custom"


class GoalStatus(str, enum.Enum):
    """Investment goal status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InvoiceStatus(str, enum.Enum):
    """Invoice payment status."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaxReportType(str, enum.Enum):
    """Tax report types."""
    FATCA = "fatca"
    CRS = "crs"
    ZAKAT = "zakat"
    ANNUAL = "annual"


class AuditAction(str, enum.Enum):
    """Audit log action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
