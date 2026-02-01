"""
Users API Endpoints
===================

User management API including:
- User CRUD operations
- KYC management
- Tax information
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AuthenticatedUser,
    BankAdmin,
    Database,
    Pagination,
    RequiredTenant,
    verify_bank_access,
)
from app.core.security import encrypt_pii
from app.models.account import UserAccount
from app.models.goal import InvestmentGoal
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.user import (
    KYCUpdate,
    TaxInfoUpdate,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserSummary,
    UserUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Create User
# =============================================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user for the bank"
)
async def create_user(
    user_data: UserCreate,
    current_user: BankAdmin,
    db: Database
):
    """Create a new user."""
    
    # Check if email exists for this bank
    existing = await db.execute(
        select(User)
        .where(User.bank_id == current_user.bank_id)
        .where(User.email == user_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "USER_EXISTS",
                "message": f"User with email '{user_data.email}' already exists"
            }
        )
    
    # Create user
    user = User(
        bank_id=current_user.bank_id,
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        nationality=user_data.nationality,
        residency_country=user_data.residency_country,
        external_id=user_data.external_id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User created: {user.id} for bank {current_user.bank_id}")
    
    return UserResponse.model_validate(user)


# =============================================================================
# Get User
# =============================================================================

@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user details",
    description="Get detailed information about a user"
)
async def get_user(
    user_id: UUID,
    current_user: AuthenticatedUser,
    db: Database
):
    """Get user details."""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    # Verify access
    await verify_bank_access(user.bank_id, current_user)
    
    # Get additional stats
    accounts_result = await db.execute(
        select(func.count(UserAccount.id), func.sum(UserAccount.balance_usd))
        .where(UserAccount.user_id == user_id)
        .where(UserAccount.is_active == True)
    )
    accounts_row = accounts_result.one()
    accounts_count = accounts_row[0] or 0
    total_aum = accounts_row[1] or 0
    
    goals_result = await db.execute(
        select(func.count(InvestmentGoal.id))
        .where(InvestmentGoal.user_id == user_id)
    )
    goals_count = goals_result.scalar() or 0
    
    response = UserDetailResponse.model_validate(user)
    response.total_aum = total_aum
    response.accounts_count = accounts_count
    response.goals_count = goals_count
    
    return response


# =============================================================================
# Update User
# =============================================================================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information"
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: BankAdmin,
    db: Database
):
    """Update user information."""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    await verify_bank_access(user.bank_id, current_user)
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User updated: {user_id}")
    
    return UserResponse.model_validate(user)


# =============================================================================
# Update KYC
# =============================================================================

@router.put(
    "/{user_id}/kyc",
    response_model=SuccessResponse,
    summary="Update KYC status",
    description="Update user's KYC verification status"
)
async def update_kyc(
    user_id: UUID,
    kyc_data: KYCUpdate,
    current_user: BankAdmin,
    db: Database
):
    """Update user KYC status."""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    await verify_bank_access(user.bank_id, current_user)
    
    # Update KYC fields
    user.kyc_status = kyc_data.kyc_status
    
    if kyc_data.emirates_id:
        user.emirates_id_encrypted = encrypt_pii(kyc_data.emirates_id)
    
    if kyc_data.iqama_number:
        user.iqama_number_encrypted = encrypt_pii(kyc_data.iqama_number)
    
    if kyc_data.kyc_status.value == "verified":
        from datetime import datetime, timezone
        user.kyc_verified_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    logger.info(f"User KYC updated: {user_id} -> {kyc_data.kyc_status}")
    
    return SuccessResponse(
        message=f"KYC status updated to '{kyc_data.kyc_status.value}'"
    )


# =============================================================================
# Update Tax Information
# =============================================================================

@router.put(
    "/{user_id}/tax-info",
    response_model=SuccessResponse,
    summary="Update tax information",
    description="Update user's tax residency information"
)
async def update_tax_info(
    user_id: UUID,
    tax_data: TaxInfoUpdate,
    current_user: AuthenticatedUser,
    db: Database
):
    """Update user tax information."""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    await verify_bank_access(user.bank_id, current_user)
    
    # Update tax fields
    user.tax_residency_countries = tax_data.tax_residency_countries
    user.us_person = tax_data.us_person
    
    if tax_data.tin_numbers:
        # Encrypt TIN numbers
        encrypted_tins = {
            country: encrypt_pii(tin)
            for country, tin in tax_data.tin_numbers.items()
        }
        user.tin_numbers_encrypted = encrypted_tins
    
    await db.commit()
    
    logger.info(f"User tax info updated: {user_id}")
    
    return SuccessResponse(message="Tax information updated successfully")


# =============================================================================
# Delete User
# =============================================================================

@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Deactivate user",
    description="Deactivate a user account (soft delete)"
)
async def deactivate_user(
    user_id: UUID,
    current_user: BankAdmin,
    db: Database
):
    """Deactivate user account."""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    await verify_bank_access(user.bank_id, current_user)
    
    user.is_active = False
    await db.commit()
    
    logger.info(f"User deactivated: {user_id}")
    
    return SuccessResponse(message="User deactivated successfully")


# =============================================================================
# Get Current User
# =============================================================================

@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get current user",
    description="Get details of the currently authenticated user"
)
async def get_current_user_details(
    current_user: AuthenticatedUser,
    db: Database
):
    """Get current user details."""
    
    result = await db.execute(
        select(User).where(User.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    # Get additional stats
    accounts_result = await db.execute(
        select(func.count(UserAccount.id), func.sum(UserAccount.balance_usd))
        .where(UserAccount.user_id == user.id)
        .where(UserAccount.is_active == True)
    )
    accounts_row = accounts_result.one()
    
    goals_result = await db.execute(
        select(func.count(InvestmentGoal.id))
        .where(InvestmentGoal.user_id == user.id)
    )
    
    response = UserDetailResponse.model_validate(user)
    response.total_aum = accounts_row[1] or 0
    response.accounts_count = accounts_row[0] or 0
    response.goals_count = goals_result.scalar() or 0
    
    return response
