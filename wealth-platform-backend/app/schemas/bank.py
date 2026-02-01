"""
Bank Schemas
============

Pydantic schemas for bank management API.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.models.base import APIStatus, BankStatus, RevenueModel


# =============================================================================
# Branding Configuration
# =============================================================================

class BrandingConfig(BaseModel):
    """White-label branding configuration."""
    
    logo_url: Optional[str] = Field(
        default="",
        max_length=500,
        description="Logo URL (HTTPS or S3)"
    )
    primary_color: str = Field(
        default="#1890ff",
        max_length=7,
        description="Primary brand color (hex)"
    )
    secondary_color: str = Field(
        default="#52c41a",
        max_length=7,
        description="Secondary color (hex)"
    )
    font_family: str = Field(
        default="Inter",
        max_length=50,
        description="Font family"
    )
    app_name: str = Field(
        default="",
        max_length=50,
        description="White-label app name"
    )
    
    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Invalid hex color format. Use #RRGGBB")
        return v.upper()
    
    @field_validator("font_family")
    @classmethod
    def validate_font(cls, v: str) -> str:
        allowed_fonts = ["Inter", "Arial", "Roboto", "Poppins", "Open Sans"]
        if v not in allowed_fonts:
            raise ValueError(f"Font must be one of: {allowed_fonts}")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "logo_url": "https://fab.ae/logo.png",
                "primary_color": "#00539F",
                "secondary_color": "#52C41A",
                "font_family": "Inter",
                "app_name": "FAB Wealth Manager"
            }
        }
    )


# =============================================================================
# Bank Admin
# =============================================================================

class BankAdminCreate(BaseModel):
    """Bank admin creation schema."""
    
    email: EmailStr = Field(..., description="Admin email address")
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Admin full name"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Phone number"
    )
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Password (12+ chars, mixed case, numbers, special)"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain special character")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "tech@fab.com",
                "full_name": "Ahmed Al Mansouri",
                "phone": "+971501234567",
                "password": "SecurePass123!"
            }
        }
    )


class BankAdminResponse(BaseModel):
    """Bank admin response schema."""
    
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Bank Create/Update
# =============================================================================

class BankCreate(BaseModel):
    """Bank registration schema."""
    
    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Bank full name"
    )
    slug: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="URL-friendly identifier"
    )
    country: str = Field(
        ...,
        max_length=2,
        description="ISO country code (AE or SA)"
    )
    revenue_model: RevenueModel = Field(
        ...,
        description="Revenue model type"
    )
    base_fee_usd: Optional[Decimal] = Field(
        None,
        ge=10,
        le=500,
        description="Annual fee per user (USD)"
    )
    aum_share_percentage: Optional[Decimal] = Field(
        None,
        ge=1,
        le=50,
        description="Platform's AUM share percentage"
    )
    branding: Optional[BrandingConfig] = Field(
        default_factory=BrandingConfig,
        description="White-label branding"
    )
    
    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]{3,50}$", v):
            raise ValueError(
                "Slug must be lowercase, 3-50 chars, alphanumeric + hyphens only"
            )
        return v.lower()
    
    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        if v.upper() not in ["AE", "SA"]:
            raise ValueError("Country must be 'AE' (UAE) or 'SA' (Saudi Arabia)")
        return v.upper()
    
    @model_validator(mode="after")
    def validate_revenue_model_config(self):
        """Validate revenue model has required fields."""
        if self.revenue_model == RevenueModel.SAAS:
            if self.base_fee_usd is None:
                raise ValueError(
                    "SaaS model requires base_fee_usd"
                )
        elif self.revenue_model == RevenueModel.HYBRID:
            if self.base_fee_usd is None or self.aum_share_percentage is None:
                raise ValueError(
                    "Hybrid model requires both base_fee_usd and aum_share_percentage"
                )
        elif self.revenue_model == RevenueModel.AUM_SHARE:
            if self.aum_share_percentage is None:
                raise ValueError(
                    "AUM Share model requires aum_share_percentage"
                )
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "First Abu Dhabi Bank",
                "slug": "fab",
                "country": "AE",
                "revenue_model": "hybrid",
                "base_fee_usd": 25.00,
                "aum_share_percentage": 20.00,
                "branding": {
                    "logo_url": "https://fab.ae/logo.png",
                    "primary_color": "#00539F",
                    "app_name": "FAB Wealth Manager"
                }
            }
        }
    )


class BankUpdate(BaseModel):
    """Bank update schema (partial)."""
    
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    base_fee_usd: Optional[Decimal] = Field(None, ge=10, le=500)
    aum_share_percentage: Optional[Decimal] = Field(None, ge=1, le=50)
    branding: Optional[BrandingConfig] = None
    analytics_access: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "branding": {
                    "primary_color": "#1890FF"
                }
            }
        }
    )


# =============================================================================
# Bank Response
# =============================================================================

class BankResponse(BaseModel):
    """Bank response schema."""
    
    id: UUID
    name: str
    slug: str
    country: str
    revenue_model: RevenueModel
    base_fee_usd: Optional[Decimal] = None
    aum_share_percentage: Optional[Decimal] = None
    branding_config: dict[str, Any]
    api_status: APIStatus
    analytics_access: bool
    status: BankStatus
    onboarded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BankRegistrationResponse(BaseModel):
    """Response after successful bank registration."""
    
    bank_id: UUID
    slug: str
    status: BankStatus
    api_key: str = Field(..., description="API key (shown only once)")
    onboarding_steps: List[str] = Field(
        default_factory=lambda: [
            "verify_email",
            "upload_licenses",
            "configure_api",
            "activate"
        ]
    )
    message: str = "Registration successful. Verification email sent."
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_id": "550e8400-e29b-41d4-a716-446655440000",
                "slug": "fab",
                "status": "pending",
                "api_key": "pk_dev_abc123...",
                "onboarding_steps": [
                    "verify_email",
                    "upload_licenses",
                    "configure_api",
                    "activate"
                ],
                "message": "Registration successful. Verification email sent."
            }
        }
    )


# =============================================================================
# Bank Dashboard
# =============================================================================

class DashboardMetrics(BaseModel):
    """Dashboard metrics."""
    
    active_users: int = Field(..., ge=0, description="Number of active users")
    total_aum: Decimal = Field(..., ge=0, description="Total AUM in USD")
    revenue_this_month: Decimal = Field(..., ge=0, description="Current month revenue")
    revenue_ytd: Decimal = Field(..., ge=0, description="Year-to-date revenue")


class RevenueBreakdown(BaseModel):
    """Revenue breakdown by type."""
    
    subscription_fees: Decimal = Field(..., ge=0, description="Subscription fee revenue")
    aum_revenue_share: Decimal = Field(..., ge=0, description="AUM share revenue")


class TopUser(BaseModel):
    """Top user summary (anonymized)."""
    
    initials: str = Field(..., description="User initials (e.g., 'A.M.')")
    aum: Decimal = Field(..., ge=0, description="User's AUM")
    revenue_contribution: Decimal = Field(..., ge=0, description="Revenue generated")


class BankDashboard(BaseModel):
    """Bank analytics dashboard response."""
    
    period: str = Field(..., description="Dashboard period (YYYY-MM)")
    metrics: DashboardMetrics
    revenue_breakdown: RevenueBreakdown
    user_growth_percentage: float = Field(
        ..., description="User growth vs previous period (%)"
    )
    aum_growth_percentage: float = Field(
        ..., description="AUM growth vs previous period (%)"
    )
    top_users: List[TopUser] = Field(
        default_factory=list, description="Top users by AUM (anonymized)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": "2026-02",
                "metrics": {
                    "active_users": 1250,
                    "total_aum": 62500000.00,
                    "revenue_this_month": 15625.00,
                    "revenue_ytd": 31250.00
                },
                "revenue_breakdown": {
                    "subscription_fees": 3125.00,
                    "aum_revenue_share": 12500.00
                },
                "user_growth_percentage": 12.5,
                "aum_growth_percentage": 8.3,
                "top_users": [
                    {"initials": "A.M.", "aum": 500000.00, "revenue_contribution": 125.00}
                ]
            }
        }
    )


# =============================================================================
# API Configuration
# =============================================================================

class BankAPIConfig(BaseModel):
    """Bank API configuration schema."""
    
    api_base_url: str = Field(
        ...,
        max_length=500,
        description="Base URL for bank's API"
    )
    client_id: Optional[str] = Field(
        None,
        max_length=255,
        description="OAuth client ID"
    )
    client_secret: Optional[str] = Field(
        None,
        max_length=255,
        description="OAuth client secret"
    )
    webhook_secret: Optional[str] = Field(
        None,
        max_length=255,
        description="Webhook signature secret"
    )
    
    @field_validator("api_base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("https://", "http://localhost")):
            raise ValueError("API URL must use HTTPS (except localhost)")
        return v.rstrip("/")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_base_url": "https://api.fab.ae/v1",
                "client_id": "wealth_platform_client",
                "client_secret": "secret123",
                "webhook_secret": "whsec_abc123"
            }
        }
    )
