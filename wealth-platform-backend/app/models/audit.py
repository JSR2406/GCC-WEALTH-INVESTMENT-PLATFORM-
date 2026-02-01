"""
Audit Log Model
===============

Comprehensive audit logging for compliance and security.
Tracks all sensitive operations across the platform.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditAction, Base, TimestampMixin, UUIDMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Audit log for compliance and security monitoring.
    
    Tracks all sensitive operations including:
    - Authentication events (login, logout, failed attempts)
    - Data access (reads of PII, exports)
    - Data modifications (creates, updates, deletes)
    - Administrative actions
    """
    
    __tablename__ = "audit_logs"
    
    # =========================================================================
    # Context
    # =========================================================================
    
    bank_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("banks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Bank context (if applicable)"
    )
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )
    
    admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Bank admin who performed the action"
    )
    
    # =========================================================================
    # Action Details
    # =========================================================================
    
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action_enum", create_constraint=True),
        nullable=False,
        index=True,
        comment="Type of action performed"
    )
    
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of resource affected (e.g., 'user', 'bank', 'account')"
    )
    
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="ID of the affected resource"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Human-readable description of the action"
    )
    
    # =========================================================================
    # Change Details
    # =========================================================================
    
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Previous values (for updates)"
    )
    
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="New values (for creates/updates)"
    )
    
    extra_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {},
        comment="Additional metadata about the action"
    )
    
    # =========================================================================
    # Request Context
    # =========================================================================
    
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Request correlation ID"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
        comment="Client IP address"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Client user agent"
    )
    
    endpoint: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="API endpoint called"
    )
    
    http_method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="HTTP method used"
    )
    
    # =========================================================================
    # Status
    # =========================================================================
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="Action status: success, failure, error"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if action failed"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Indexes for common queries
        Index("idx_audit_bank_id", "bank_id"),
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_created", "created_at"),
        
        # Composite indexes
        Index("idx_audit_bank_action", "bank_id", "action"),
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_bank_time", "bank_id", "created_at"),
        
        # Time-based partitioning hint
        {"comment": "Audit logs for compliance and security monitoring"}
    )
    
    # =========================================================================
    # Factory Methods
    # =========================================================================
    
    @classmethod
    def create_login_event(
        cls,
        user_id: uuid.UUID,
        bank_id: uuid.UUID,
        ip_address: str,
        user_agent: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> "AuditLog":
        """Create a login audit event."""
        return cls(
            user_id=user_id,
            bank_id=bank_id,
            action=AuditAction.LOGIN,
            resource_type="user",
            resource_id=str(user_id),
            description="User login attempt",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure",
            error_message=error_message
        )
    
    @classmethod
    def create_data_access_event(
        cls,
        user_id: uuid.UUID,
        bank_id: uuid.UUID,
        resource_type: str,
        resource_id: str,
        description: str,
        request_id: Optional[str] = None
    ) -> "AuditLog":
        """Create a data access audit event."""
        return cls(
            user_id=user_id,
            bank_id=bank_id,
            action=AuditAction.READ,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            request_id=request_id,
            status="success"
        )
    
    @classmethod
    def create_modification_event(
        cls,
        user_id: uuid.UUID,
        bank_id: uuid.UUID,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        description: str,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        request_id: Optional[str] = None
    ) -> "AuditLog":
        """Create a data modification audit event."""
        return cls(
            user_id=user_id,
            bank_id=bank_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            request_id=request_id,
            status="success"
        )
