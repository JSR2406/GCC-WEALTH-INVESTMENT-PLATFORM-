"""
Investment Goal Model
=====================

Goal-based investing targets for users.
Tracks progress towards financial goals.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GoalStatus, GoalType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.bank import Bank
    from app.models.user import User


class InvestmentGoal(Base, UUIDMixin, TimestampMixin):
    """
    User's investment goal.
    
    Enables goal-based investing with target tracking and
    automated portfolio recommendations.
    """
    
    __tablename__ = "investment_goals"
    
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
        comment="Goal owner"
    )
    
    # =========================================================================
    # Goal Details
    # =========================================================================
    
    goal_type: Mapped[GoalType] = mapped_column(
        Enum(GoalType, name="goal_type_enum", create_constraint=True),
        nullable=False,
        comment="Type of investment goal"
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Custom goal name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Goal description"
    )
    
    # =========================================================================
    # Target & Progress
    # =========================================================================
    
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        comment="Target amount to achieve (USD)"
    )
    
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Current progress amount (USD)"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="Currency for the goal"
    )
    
    target_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Target date to achieve goal"
    )
    
    # =========================================================================
    # Contributions
    # =========================================================================
    
    monthly_contribution: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Recommended monthly contribution"
    )
    
    auto_invest: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether automatic investing is enabled"
    )
    
    # =========================================================================
    # Investment Allocation
    # =========================================================================
    
    portfolio_allocation: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {},
        comment="Asset allocation for this goal"
    )
    
    # Example allocation:
    # {
    #   "stocks": 60,
    #   "bonds": 30,
    #   "cash": 10,
    #   "recommended_funds": ["VTSAX", "BND"]
    # }
    
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Risk level: conservative, moderate, aggressive"
    )
    
    # =========================================================================
    # Status
    # =========================================================================
    
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status_enum", create_constraint=True),
        nullable=False,
        default=GoalStatus.ACTIVE,
        index=True,
        comment="Goal status"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When goal was completed"
    )
    
    # =========================================================================
    # Visual Customization
    # =========================================================================
    
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="target",
        comment="Icon identifier for UI"
    )
    
    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        default="#1890ff",
        comment="Color hex code for UI"
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
        back_populates="goals",
        lazy="selectin"
    )
    
    # =========================================================================
    # Table Configuration
    # =========================================================================
    
    __table_args__ = (
        # Indexes
        Index("idx_goals_bank_id", "bank_id"),
        Index("idx_goals_user_id", "user_id"),
        Index("idx_goals_status", "status"),
        Index("idx_goals_type", "goal_type"),
        Index("idx_goals_target_date", "target_date"),
        
        # Composite indexes
        Index("idx_goals_user_status", "user_id", "status"),
        
        # Check constraints
        CheckConstraint(
            "target_amount > 0",
            name="ck_goals_target_positive"
        ),
        CheckConstraint(
            "current_amount >= 0",
            name="ck_goals_current_non_negative"
        ),
        
        {"comment": "User investment goals for goal-based investing"}
    )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.target_amount == 0:
            return 0
        return min(100, float(self.current_amount / self.target_amount * 100))
    
    @property
    def remaining_amount(self) -> Decimal:
        """Get remaining amount to reach goal."""
        return max(Decimal(0), self.target_amount - self.current_amount)
    
    @property
    def is_completed(self) -> bool:
        """Check if goal is completed."""
        return self.status == GoalStatus.COMPLETED or self.current_amount >= self.target_amount
    
    @property
    def is_on_track(self) -> bool:
        """Check if goal is on track based on timeline."""
        from datetime import date as date_type
        
        today = date_type.today()
        if today >= self.target_date:
            return self.is_completed
        
        # Calculate expected progress based on time
        total_days = (self.target_date - self.created_at.date()).days
        days_passed = (today - self.created_at.date()).days
        
        if total_days <= 0:
            return True
        
        expected_progress = days_passed / total_days * 100
        return self.progress_percentage >= expected_progress * 0.9  # 10% buffer
    
    @property
    def months_remaining(self) -> int:
        """Get months remaining until target date."""
        from datetime import date as date_type
        
        today = date_type.today()
        if today >= self.target_date:
            return 0
        
        months = (self.target_date.year - today.year) * 12
        months += self.target_date.month - today.month
        return max(0, months)
