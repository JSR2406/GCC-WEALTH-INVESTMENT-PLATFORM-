"""
GCC Wealth Platform Backend
============================

FastAPI application with simplified auth for demo purposes.
"""

import logging
import base64
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from jose import jwt

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Auth Schemas
# =============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    bank_slug: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    bank_id: str
    bank_slug: str
    kyc_status: str
    subscription_tier: str
    is_active: bool


class AuthResponse(BaseModel):
    user: UserProfileResponse
    tokens: TokenResponse


# =============================================================================
# Mock Users Database
# =============================================================================

MOCK_USERS = {
    "fab": {
        "demo@fab.ae": {
            "id": "user-fab-001",
            "email": "demo@fab.ae",
            "password": "demo123",
            "full_name": "Ahmed Al-Zahrani",
            "bank_id": "fab-001",
            "bank_slug": "fab",
            "kyc_status": "verified",
            "subscription_tier": "premium",
            "is_active": True
        },
    },
    "hsbc": {
        "john@example.com": {
            "id": "user-hsbc-001",
            "email": "john@example.com",
            "password": "demo123",
            "full_name": "John Smith",
            "bank_id": "hsbc-001",
            "bank_slug": "hsbc",
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
            "kyc_status": "verified",
            "subscription_tier": "premium",
            "is_active": True
        }
    }
}


# =============================================================================
# Token Functions
# =============================================================================

def create_token(user_id: str, token_type: str = "access", **extra_claims):
    """Create JWT token."""
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    payload = {
        "sub": user_id,
        "type": token_type,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        **extra_claims
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except Exception:
        return None


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting GCC Wealth Platform Backend")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("👋 Shutting down GCC Wealth Platform Backend")


# =============================================================================
# App
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Cross-border wealth management platform for GCC banks",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =============================================================================
# Auth Endpoints
# =============================================================================

@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(credentials: LoginRequest):
    """Authenticate user and return tokens."""
    bank_users = MOCK_USERS.get(credentials.bank_slug, {})
    user = bank_users.get(credentials.email)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        )
    
    access_token = create_token(
        user["id"],
        "access",
        email=user["email"],
        bank_id=user["bank_id"],
        bank_slug=user["bank_slug"]
    )
    refresh_token = create_token(user["id"], "refresh")
    
    logger.info(f"User logged in: {user['email']}")
    
    return AuthResponse(
        user=UserProfileResponse(**{k: v for k, v in user.items() if k != "password"}),
        tokens=TokenResponse(access_token=access_token, refresh_token=refresh_token)
    )


@app.post("/api/v1/auth/logout", tags=["Authentication"])
async def logout():
    """Logout user."""
    return {"message": "Logged out successfully"}


@app.get("/api/v1/auth/me", response_model=UserProfileResponse, tags=["Authentication"])
async def get_me(authorization: Optional[str] = Header(None)):
    """Get current user from token."""
    if not authorization:
        raise HTTPException(status_code=401, detail={"code": "NOT_AUTHENTICATED", "message": "Not authenticated"})
    
    token = authorization.replace("Bearer ", "")
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid token"})
    
    user_id = payload.get("sub")
    for bank_users in MOCK_USERS.values():
        for user in bank_users.values():
            if user["id"] == user_id:
                return UserProfileResponse(**{k: v for k, v in user.items() if k != "password"})
    
    raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "User not found"})


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    return {"service": settings.APP_NAME, "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


# =============================================================================
# Mock Data
# =============================================================================

MOCK_BANKS = [
    {"id": "fab-001", "name": "First Abu Dhabi Bank", "slug": "fab", "country": "AE",
     "branding": {"primary_color": "#00A651", "secondary_color": "#003366", "app_name": "FAB Wealth"},
     "features": {"sharia_products": True, "zakat_calculator": True}},
    {"id": "hsbc-001", "name": "HSBC Middle East", "slug": "hsbc", "country": "AE",
     "branding": {"primary_color": "#DB0011", "secondary_color": "#2E2E2E", "app_name": "HSBC Wealth"},
     "features": {"sharia_products": False, "zakat_calculator": False}},
    {"id": "rajhi-001", "name": "Al Rajhi Bank", "slug": "rajhi", "country": "SA",
     "branding": {"primary_color": "#004B87", "secondary_color": "#00A0DF", "app_name": "Al Rajhi Wealth"},
     "features": {"sharia_products": True, "zakat_calculator": True}},
]

MOCK_GOALS = [
    {"id": "goal-001", "name": "Retirement at 55", "type": "retirement", "target_amount": 1000000, 
     "current_amount": 680000, "progress": 68, "status": "active"},
    {"id": "goal-002", "name": "Children's Education", "type": "education", "target_amount": 200000,
     "current_amount": 95000, "progress": 47.5, "status": "active"},
]


# =============================================================================
# Data Endpoints
# =============================================================================

@app.get("/api/v1/banks", tags=["Banks"])
async def list_banks():
    return {"data": MOCK_BANKS, "total": len(MOCK_BANKS)}


@app.get("/api/v1/banks/{bank_slug}", tags=["Banks"])
async def get_bank(bank_slug: str):
    for bank in MOCK_BANKS:
        if bank["slug"] == bank_slug:
            return bank
    return JSONResponse(status_code=404, content={"code": "BANK_NOT_FOUND", "message": f"Bank '{bank_slug}' not found"})


@app.get("/api/v1/portfolio/summary", tags=["Portfolio"])
async def get_portfolio_summary():
    return {
        "total_aum": 575000, "currency": "USD", "change_24h": 2.5, "change_7d": 4.2,
        "accounts": [
            {"type": "savings", "balance": 125000, "currency": "AED", "percentage": 21.7},
            {"type": "investment", "balance": 450000, "currency": "USD", "percentage": 78.3}
        ],
        "allocation": {"equity": 45, "fixed_income": 30, "real_estate": 15, "cash": 10}
    }


@app.get("/api/v1/goals", tags=["Goals"])
async def list_goals():
    return {"data": MOCK_GOALS, "total": len(MOCK_GOALS), "summary": {"total_target": 1200000, "overall_progress": 64.6}}


@app.get("/api/v1/tax/reports", tags=["Tax"])
async def get_tax_reports():
    return {
        "reports": [
            {"type": "fatca", "name": "FATCA Report 2025", "status": "submitted", "deadline": "2026-03-31"},
            {"type": "crs", "name": "CRS Report 2025", "status": "pending", "deadline": "2026-06-30"}
        ],
        "zakat": {"enabled": True, "zakatable_wealth": 575000, "zakat_due": 14375, "nisab_threshold": 5500}
    }


@app.get("/api/v1/analytics/overview", tags=["Analytics"])
async def get_analytics_overview():
    return {
        "total_users": 15420, "total_aum": 2500000000, "active_banks": 3,
        "monthly_revenue": 125000, "user_growth": 12.5, "aum_growth": 8.3
    }


logger.info("✅ GCC Wealth Platform Backend initialized")
