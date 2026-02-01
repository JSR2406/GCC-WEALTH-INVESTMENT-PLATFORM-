from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.fee_service import FeeService, PaymentFailedError, RefundFailedError
from app.schemas.fee import *
from app.models.user import User
from app.models.service_fee import ServiceFeeConfig, ServiceCharge, UserSubscription
from app.api.deps import get_db, get_current_user
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID

router = APIRouter()

@router.get("/configs", response_model=List[FeeConfigResponse])
async def list_fee_configs(
    category: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available fee configurations.
    
    Use this endpoint to show users what services have fees.
    """
    query = select(ServiceFeeConfig).where(ServiceFeeConfig.is_active == is_active)
    
    if category:
        query = query.where(ServiceFeeConfig.category == category)
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    return configs


@router.post("/calculate", response_model=FeeCalculation)
async def calculate_fee(
    request: FeeCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate fee for a service before charging.
    """
    fee_service = FeeService(db)
    
    try:
        calculation = await fee_service.calculate_service_fee(
            fee_code=request.fee_code,
            base_amount=request.base_amount or Decimal("0.00"),
            quantity=request.quantity or 1,
            user_id=current_user.id
        )
        return calculation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/charge", response_model=ServiceChargeResponse)
async def charge_service_fee(
    request: ChargeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Charge service fee to user's payment method.
    """
    fee_service = FeeService(db)
    
    try:
        charge = await fee_service.charge_fee(
            fee_code=request.fee_code,
            user_id=current_user.id,
            quantity=request.quantity or 1,
            payment_method_id=request.payment_method_id,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            metadata=request.metadata
        )
        
        return charge
    
    except PaymentFailedError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/my-charges", response_model=List[ServiceChargeResponse])
async def get_my_charges(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's service charge history.
    """
    fee_service = FeeService(db)
    
    charges = await fee_service.get_user_charges(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if category:
        charges = [c for c in charges if c.category == category]
    
    return charges


@router.post("/charges/{charge_id}/refund")
async def request_refund(
    charge_id: UUID,
    request: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request refund for a service charge.
    """
    fee_service = FeeService(db)
    
    # Verify charge belongs to user
    charge = await db.get(ServiceCharge, charge_id)
    if not charge or charge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Charge not found")
    
    try:
        refunded_charge = await fee_service.refund_charge(
            charge_id=charge_id,
            amount=request.amount,
            reason=request.reason
        )
        
        return {
            "message": "Refund processed successfully",
            "refund_amount": float(refunded_charge.refund_amount),
            "refunded_at": refunded_charge.refunded_at.isoformat()
        }
    
    except RefundFailedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estimate", response_model=FeeEstimate)
async def estimate_monthly_fees(
    tax_reports: int = Query(0, ge=0),
    instant_syncs: int = Query(0, ge=0),
    ai_recommendations: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Estimate monthly fees based on projected usage.
    """
    fee_service = FeeService(db)
    
    usage_projection = {}
    if tax_reports > 0:
        usage_projection["tax_reports"] = tax_reports
    if instant_syncs > 0:
        usage_projection["instant_syncs"] = instant_syncs
    if ai_recommendations > 0:
        usage_projection["ai_recommendations"] = ai_recommendations
    
    estimate = await fee_service.estimate_monthly_fees(
        user_id=current_user.id,
        usage_projection=usage_projection
    )
    
    return estimate


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe_to_premium(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to premium features.
    """
    # Check if plan exists (mapping plan_code to fee_code)
    # Using simple mapping for now
    fee_code = request.plan_code
    
    result = await db.execute(select(ServiceFeeConfig).where(ServiceFeeConfig.fee_code == fee_code))
    fee_config = result.scalar_one_or_none()
    
    if not fee_config:
        raise HTTPException(status_code=404, detail=f"Plan {fee_code} not found")

    if fee_config.fee_type != FeeType.SUBSCRIPTION:
         raise HTTPException(status_code=400, detail="Not a subscription plan")

    # In a real implementation we would create a Stripe Subscription here
    # For now we will mock the creation of a subscription record
    
    now = datetime.now(timezone.utc)
    # Default to monthly
    period_days = 365 if fee_config.billing_cycle == 'annual' else 30
    
    subscription = UserSubscription(
        user_id=current_user.id,
        fee_config_id=fee_config.id,
        subscription_name=fee_config.fee_name,
        status="active",
        billing_cycle=fee_config.billing_cycle or "monthly",
        amount=fee_config.base_amount,
        currency=fee_config.currency,
        current_period_start=now,
        current_period_end=now + timedelta(days=period_days),
        stripe_subscription_id=f"sub_mock_{uuid.uuid4().hex[:8]}" 
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    return subscription
