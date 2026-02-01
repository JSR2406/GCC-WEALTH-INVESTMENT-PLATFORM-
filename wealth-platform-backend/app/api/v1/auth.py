"""
Authentication API Endpoints
============================

Handles user authentication including:
- Login with email/password
- Token refresh
- Logout
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr, Field

from app.core.security import create_access_token, create_refresh_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    bank_slug: str = Field(..., description="Bank tenant slug")


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserProfileResponse(BaseModel):
    """User profile in auth response."""
    id: str
    email: str
    full_name: str
    bank_id: str
    bank_slug: str
    kyc_status: str
    subscription_tier: str
    is_active: bool


class AuthResponse(BaseModel):
    """Full authentication response."""
    user: UserProfileResponse
    tokens: TokenResponse


# =============================================================================
# Mock Users Database
# =============================================================================

MOCK_USERS = {
    "fab": {
        "ahmed@example.com": {
            "id": "user-fab-001",
            "email": "ahmed@example.com",
            "password": "demo123",  # In real app, this would be hashed
            "full_name": "Ahmed Al-Zahrani",
            "bank_id": "fab-001",
            "bank_slug": "fab",
            "nationality": "SA",
            "residency_country": "AE",
            "kyc_status": "verified",
            "subscription_tier": "premium",
            "is_active": True
        },
        "demo@fab.ae": {
            "id": "user-fab-002",
            "email": "demo@fab.ae",
            "password": "demo123",
            "full_name": "Demo User",
            "bank_id": "fab-001",
            "bank_slug": "fab",
            "nationality": "AE",
            "residency_country": "AE",
            "kyc_status": "verified",
            "subscription_tier": "basic",
            "is_active": True
        }
    },
    "hsbc": {
        "john@example.com": {
            "id": "user-hsbc-001",
            "email": "john@example.com",
            "password": "demo123",
            "full_name": "John Smith",
            "bank_id": "hsbc-001",
            "bank_slug": "hsbc",
            "nationality": "GB",
            "residency_country": "AE",
            "kyc_status": "verified",
            "subscription_tier": "premium",
            "is_active": True
        }
    },
    "rajhi": {
        "mohammed@example.com": {
            "id": "user-rajhi-001",
            "email": "mohammed@example.com",
            "password": "demo123",
            "full_name": "محمد الراجحي",
            "bank_id": "rajhi-001",
            "bank_slug": "rajhi",
            "nationality": "SA",
            "residency_country": "SA",
            "kyc_status": "verified",
            "subscription_tier": "premium",
            "is_active": True
        }
    }
}


# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user and return tokens"
)
async def login(credentials: LoginRequest):
    """Authenticate user and return JWT tokens."""
    
    # Find user in mock database
    bank_users = MOCK_USERS.get(credentials.bank_slug, {})
    user = bank_users.get(credentials.email)
    
    if not user:
        logger.warning(f"Login failed: user not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )
    
    # Verify password (in real app, use password hashing)
    if user["password"] != credentials.password:
        logger.warning(f"Login failed: wrong password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS", 
                "message": "Invalid email or password"
            }
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_DISABLED",
                "message": "Account is disabled"
            }
        )
    
    # Create tokens
    additional_claims = {
        "email": user["email"],
        "bank_id": user["bank_id"],
        "bank_slug": user["bank_slug"],
        "role": "user",
        "permissions": ["view_portfolio", "manage_goals", "view_tax"]
    }
    
    access_token = create_access_token(user["id"], additional_claims)
    refresh_token = create_refresh_token(user["id"])
    
    logger.info(f"User logged in: {user['email']} ({credentials.bank_slug})")
    
    return AuthResponse(
        user=UserProfileResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            bank_id=user["bank_id"],
            bank_slug=user["bank_slug"],
            kyc_status=user["kyc_status"],
            subscription_tier=user["subscription_tier"],
            is_active=user["is_active"]
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(request: RefreshRequest):
    """Refresh access token."""
    
    try:
        payload = verify_token(request.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Invalid refresh token"}
            )
        
        # Find user by ID (simplified for mock)
        user = None
        for bank_users in MOCK_USERS.values():
            for u in bank_users.values():
                if u["id"] == user_id:
                    user = u
                    break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "USER_NOT_FOUND", "message": "User not found"}
            )
        
        # Create new tokens
        additional_claims = {
            "email": user["email"],
            "bank_id": user["bank_id"],
            "bank_slug": user["bank_slug"],
            "role": "user",
            "permissions": ["view_portfolio", "manage_goals", "view_tax"]
        }
        
        new_access_token = create_access_token(user["id"], additional_claims)
        new_refresh_token = create_refresh_token(user["id"])
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired refresh token"}
        )


@router.post(
    "/logout",
    summary="User logout",
    description="Invalidate user session"
)
async def logout():
    """Logout user (client should discard tokens)."""
    # In a real app, you'd add the token to a blacklist
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user",
    description="Get authenticated user profile"
)
async def get_me(authorization: str = Header(None)):
    """Get current authenticated user."""
    
    # This is simplified - in real app, use dependency injection
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "NOT_AUTHENTICATED", "message": "Not authenticated"}
        )
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token, token_type="access")
        
        user_id = payload.get("sub")
        
        # Find user
        for bank_users in MOCK_USERS.values():
            for user in bank_users.values():
                if user["id"] == user_id:
                    return UserProfileResponse(
                        id=user["id"],
                        email=user["email"],
                        full_name=user["full_name"],
                        bank_id=user["bank_id"],
                        bank_slug=user["bank_slug"],
                        kyc_status=user["kyc_status"],
                        subscription_tier=user["subscription_tier"],
                        is_active=user["is_active"]
                    )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
        
    except Exception as e:
        logger.error(f"Auth check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid token"}
        )
