from sqlalchemy import Column, String, Numeric, Boolean, JSON, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin
import uuid
from enum import Enum
from decimal import Decimal

class FeeType(str, Enum):
    """Types of fees the platform can charge."""
    FLAT = "flat"                          # Fixed amount (e.g., $19.99)
    PERCENTAGE = "percentage"              # Percentage of transaction (e.g., 2.5%)
    TIERED = "tiered"                      # Volume-based tiers
    SUBSCRIPTION = "subscription"          # Recurring monthly/annual
    API_USAGE = "api_usage"               # Per API call above threshold

class FeeCategory(str, Enum):
    """Categories of chargeable services."""
    PREMIUM_FEATURE = "premium_feature"    # Premium app features
    TAX_REPORT = "tax_report"             # Tax document generation
    INSTANT_SYNC = "instant_sync"         # Real-time account sync
    AI_ADVISORY = "ai_advisory"           # AI recommendations
    PRIORITY_SUPPORT = "priority_support" # Priority customer support
    DOCUMENT_EXPORT = "document_export"   # PDF/CSV exports
    TRANSACTION = "transaction"           # Payment transactions
    API_CALL = "api_call"                # API usage fees
    CURRENCY_CONVERSION = "currency_conversion"
    WITHDRAWAL = "withdrawal"

class ChargeableEntity(str, Enum):
    """Who gets charged the fee."""
    END_USER = "end_user"                 # Charge to end user
    BANK = "bank"                         # Charge to bank partner
    SPLIT = "split"                       # Split between user and bank

class ServiceFeeConfig(Base, UUIDMixin, TimestampMixin):
    """
    Configuration for platform service charges.
    
    Defines what services have fees and how they're calculated.
    """
    __tablename__ = "service_fee_configs"
    
    # Fee identification
    fee_name = Column(String(255), nullable=False)
    fee_code = Column(String(50), unique=True, nullable=False)  # e.g., "TAX_REPORT_FATCA"
    category = Column(SQLEnum(FeeCategory), nullable=False)
    
    # Fee structure
    fee_type = Column(SQLEnum(FeeType), nullable=False)
    base_amount = Column(Numeric(10, 2), nullable=True)  # For flat fees
    percentage = Column(Numeric(5, 2), nullable=True)     # For percentage fees
    
    # Tiered pricing (for volume-based fees)
    tier_config = Column(JSON, nullable=True)
    # Example: {
    #   "tiers": [
    #     {"min": 0, "max": 1000, "rate": 0.01},
    #     {"min": 1001, "max": 10000, "rate": 0.008},
    #     {"min": 10001, "max": null, "rate": 0.005}
    #   ]
    # }
    
    # Who pays
    chargeable_to = Column(SQLEnum(ChargeableEntity), nullable=False)
    split_percentage = Column(Numeric(5, 2), nullable=True)  # If split, user's %
    
    # Currency and limits
    currency = Column(String(3), nullable=False, default="USD")
    minimum_charge = Column(Numeric(10, 2), nullable=True)
    maximum_charge = Column(Numeric(10, 2), nullable=True)
    
    # Free tier (for API usage, etc.)
    free_tier_limit = Column(Numeric(10, 0), nullable=True)  # e.g., 1000 free API calls
    
    # Billing
    billing_cycle = Column(String(20), nullable=True)  # 'monthly', 'annual', 'one_time'
    
    # Availability
    is_active = Column(Boolean, default=True)
    is_optional = Column(Boolean, default=True)  # Can user opt out?
    
    # Description for transparency
    description = Column(String(500), nullable=False)
    terms_url = Column(String(500), nullable=True)
    
    # Bank-specific overrides
    allows_bank_override = Column(Boolean, default=False)  # Can banks set their own fees?
    
    def calculate_fee(self, base_value: Decimal, quantity: int = 1) -> Decimal:
        """
        Calculate fee based on configuration.
        
        Args:
            base_value: Transaction amount or base value
            quantity: Number of items (for per-unit fees)
        
        Returns:
            Calculated fee amount
        """
        if self.fee_type == FeeType.FLAT:
            fee = Decimal(self.base_amount or 0) * quantity
        
        elif self.fee_type == FeeType.PERCENTAGE:
            fee = base_value * (Decimal(self.percentage or 0) / 100)
        
        elif self.fee_type == FeeType.TIERED:
            fee = self._calculate_tiered_fee(base_value)
        
        elif self.fee_type == FeeType.SUBSCRIPTION:
            fee = Decimal(self.base_amount or 0)
        
        elif self.fee_type == FeeType.API_USAGE:
            limit = self.free_tier_limit or 0
            if quantity <= limit:
                fee = Decimal("0.00")
            else:
                billable_quantity = quantity - limit
                fee = Decimal(self.base_amount or 0) * billable_quantity
        
        else:
            fee = Decimal("0.00")
        
        # Apply min/max constraints
        if self.minimum_charge:
            fee = max(fee, Decimal(self.minimum_charge))
        if self.maximum_charge:
            fee = min(fee, Decimal(self.maximum_charge))
        
        return fee
    
    def _calculate_tiered_fee(self, base_value: Decimal) -> Decimal:
        """Calculate fee using tiered pricing."""
        if not self.tier_config or "tiers" not in self.tier_config:
            return Decimal("0.00")
        
        total_fee = Decimal("0.00")
        remaining = base_value
        
        for tier in self.tier_config["tiers"]:
            tier_min = Decimal(tier["min"])
            tier_max = Decimal(tier["max"]) if tier.get("max") else None
            rate = Decimal(tier["rate"])
            
            if remaining <= 0:
                break
            
            # Calculate amount in this tier
            tier_size = (tier_max - tier_min) if tier_max else None
            
            if tier_size is not None:
                amount_in_tier = min(remaining, tier_size)
            else:
                amount_in_tier = remaining
            
            tier_fee = amount_in_tier * rate
            total_fee += tier_fee
            remaining -= amount_in_tier
        
        return total_fee


class ServiceCharge(Base, UUIDMixin, TimestampMixin):
    """
    Record of actual service charges applied to users/banks.
    """
    __tablename__ = "service_charges"
    
    # What was charged
    fee_config_id = Column(UUID(as_uuid=True), ForeignKey('service_fee_configs.id'), nullable=False)
    fee_name = Column(String(255), nullable=False)
    category = Column(SQLEnum(FeeCategory), nullable=False)
    
    # Who was charged
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    bank_id = Column(UUID(as_uuid=True), ForeignKey('banks.id'), nullable=True)
    
    # Charge details
    base_amount = Column(Numeric(18, 2), nullable=False)  # Original transaction amount
    fee_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Split charges (if applicable)
    user_portion = Column(Numeric(10, 2), nullable=True)
    bank_portion = Column(Numeric(10, 2), nullable=True)
    
    # Payment tracking
    payment_status = Column(String(20), nullable=False, default="pending")
    # pending, authorized, captured, failed, refunded
    
    stripe_charge_id = Column(String(255), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Reference to what triggered the charge
    reference_type = Column(String(50), nullable=True)  # 'goal', 'tax_report', 'api_call'
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Refund tracking
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_reason = Column(String(500), nullable=True)
    
    # Relationships
    fee_config = relationship("ServiceFeeConfig", backref="charges")
    user = relationship("User", backref="service_charges")
    bank = relationship("Bank", backref="service_charges")


class UserSubscription(Base, UUIDMixin, TimestampMixin):
    """
    Track user subscriptions to premium features.
    """
    __tablename__ = "user_subscriptions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    fee_config_id = Column(UUID(as_uuid=True), ForeignKey('service_fee_configs.id'), nullable=False)
    
    # Subscription details
    subscription_name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    # active, canceled, past_due, trialing
    
    # Billing
    billing_cycle = Column(String(20), nullable=False)  # 'monthly', 'annual'
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Dates
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="subscriptions")
    fee_config = relationship("ServiceFeeConfig", backref="subscriptions")
