from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from app.models.service_fee import FeeCategory, FeeType, ChargeableEntity

class FeeConfigResponse(BaseModel):
    id: UUID
    fee_name: str
    fee_code: str
    category: FeeCategory
    fee_type: FeeType
    base_amount: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    chargeable_to: ChargeableEntity
    currency: str
    billing_cycle: Optional[str] = None
    description: str
    is_optional: bool
    minimum_charge: Optional[Decimal] = None
    maximum_charge: Optional[Decimal] = None
    free_tier_limit: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)

class FeeCalculationRequest(BaseModel):
    fee_code: str
    base_amount: Optional[Decimal] = Decimal("0.00")
    quantity: Optional[int] = 1

class FeeBreakdown(BaseModel):
    base_amount: float
    quantity: int
    fee_type: FeeType
    rate: Optional[float] = None

class FeeCalculation(BaseModel):
    fee_amount: float
    currency: str
    description: str
    chargeable_to: ChargeableEntity
    is_optional: bool
    breakdown: Optional[FeeBreakdown] = None
    user_portion: Optional[float] = 0.0
    bank_portion: Optional[float] = 0.0

class ChargeRequest(BaseModel):
    fee_code: str
    quantity: Optional[int] = 1
    payment_method_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class ServiceChargeResponse(BaseModel):
    charge_id: UUID = Field(..., validation_alias="id")
    amount: float = Field(..., validation_alias="fee_amount")
    currency: str
    status: str = Field(..., validation_alias="payment_status")
    stripe_charge_id: Optional[str] = None
    charged_at: datetime = Field(..., validation_alias="created_at")
    
    # Additional fields
    fee_name: Optional[str] = None
    category: Optional[FeeCategory] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class RefundRequest(BaseModel):
    reason: str
    amount: Optional[Decimal] = None

class FeeEstimateBreakdownItem(BaseModel):
    quantity: int
    unit_price: float
    total: float

class FeeEstimate(BaseModel):
    estimated_monthly_total: float
    currency: str
    breakdown: Dict[str, FeeEstimateBreakdownItem]

class SubscriptionRequest(BaseModel):
    plan_code: str
    payment_method_id: str

class SubscriptionResponse(BaseModel):
    id: UUID
    subscription_name: str
    status: str
    amount: Decimal
    currency: str
    current_period_end: datetime
    
    model_config = ConfigDict(from_attributes=True)
