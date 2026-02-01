"""
User Schemas
============

Pydantic schemas for user management API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.base import KYCStatus, SubscriptionTier


# =============================================================================
# User Create/Update
# =============================================================================

class UserCreate(BaseModel):
    """User creation schema."""
    
    email: EmailStr = Field(..., description="User email address")
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Phone number with country code"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full legal name"
    )
    nationality: str = Field(
        ...,
        max_length=2,
        description="ISO 3166-1 alpha-2 nationality"
    )
    residency_country: str = Field(
        ...,
        max_length=2,
        description="Country of residence (AE or SA)"
    )
    external_id: Optional[str] = Field(
        None,
        max_length=255,
        description="External ID from bank's system"
    )
    
    @field_validator("residency_country")
    @classmethod
    def validate_residency(cls, v: str) -> str:
        if v.upper() not in ["AE", "SA"]:
            raise ValueError("Residency must be 'AE' (UAE) or 'SA' (Saudi Arabia)")
        return v.upper()
    
    @field_validator("nationality")
    @classmethod
    def validate_nationality(cls, v: str) -> str:
        # Basic ISO 3166-1 alpha-2 validation
        if len(v) != 2 or not v.isalpha():
            raise ValueError("Nationality must be a 2-letter ISO country code")
        return v.upper()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "phone": "+971501234567",
                "full_name": "Mohammed Ahmed",
                "nationality": "AE",
                "residency_country": "AE",
                "external_id": "CUST-123456"
            }
        }
    )


class UserUpdate(BaseModel):
    """User update schema (partial)."""
    
    phone: Optional[str] = Field(None, max_length=20)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    subscription_tier: Optional[SubscriptionTier] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subscription_tier": "premium"
            }
        }
    )


# =============================================================================
# KYC
# =============================================================================

class KYCDocument(BaseModel):
    """KYC document reference."""
    
    document_type: str = Field(
        ...,
        description="Document type (emirates_id, iqama, passport)"
    )
    document_url: str = Field(
        ...,
        max_length=500,
        description="S3 URL of document"
    )
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    verified: bool = Field(default=False, description="Whether verified")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_type": "emirates_id",
                "document_url": "https://s3.amazonaws.com/docs/eid_123.pdf",
                "uploaded_at": "2026-01-15T10:30:00Z",
                "verified": True
            }
        }
    )


class KYCUpdate(BaseModel):
    """KYC status update schema."""
    
    kyc_status: KYCStatus = Field(..., description="New KYC status")
    emirates_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Emirates ID number (will be encrypted)"
    )
    iqama_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Saudi Iqama number (will be encrypted)"
    )
    rejection_reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for rejection (if applicable)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kyc_status": "verified",
                "emirates_id": "784-1990-1234567-1"
            }
        }
    )


# =============================================================================
# Tax Information
# =============================================================================

class TaxInfoUpdate(BaseModel):
    """User tax information update."""
    
    tax_residency_countries: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Countries of tax residency"
    )
    us_person: bool = Field(
        ...,
        description="Whether user is a US person (FATCA)"
    )
    tin_numbers: Optional[dict[str, str]] = Field(
        None,
        description="Tax identification numbers by country"
    )
    
    @field_validator("tax_residency_countries")
    @classmethod
    def validate_countries(cls, v: List[str]) -> List[str]:
        return [c.upper() for c in v if len(c) == 2 and c.isalpha()]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tax_residency_countries": ["AE", "GB"],
                "us_person": False,
                "tin_numbers": {"GB": "12345678"}
            }
        }
    )


# =============================================================================
# User Response
# =============================================================================

class UserResponse(BaseModel):
    """User response schema."""
    
    id: UUID
    bank_id: UUID
    email: str
    phone: Optional[str] = None
    full_name: str
    nationality: str
    residency_country: str
    kyc_status: KYCStatus
    subscription_tier: SubscriptionTier
    is_active: bool
    onboarded_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """Detailed user response with additional fields."""
    
    external_id: Optional[str] = None
    tax_residency_countries: List[str] = Field(default_factory=list)
    us_person: bool = False
    kyc_documents: List[dict] = Field(default_factory=list)
    risk_profile: Optional[dict] = None
    total_aum: Decimal = Field(default=Decimal(0))
    accounts_count: int = Field(default=0)
    goals_count: int = Field(default=0)


# =============================================================================
# User Summary (for lists)
# =============================================================================

class UserSummary(BaseModel):
    """Compact user summary for lists."""
    
    id: UUID
    email: str
    full_name: str
    kyc_status: KYCStatus
    subscription_tier: SubscriptionTier
    is_active: bool
    last_active: Optional[datetime] = None
    total_aum: Decimal = Field(default=Decimal(0))
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# User Analytics
# =============================================================================

class UserAnalytics(BaseModel):
    """User analytics/metrics."""
    
    user_id: UUID
    total_aum: Decimal
    aum_change_30d: Decimal
    aum_change_percentage: float
    total_goals: int
    completed_goals: int
    active_accounts: int
    last_activity: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_aum": 250000.00,
                "aum_change_30d": 12500.00,
                "aum_change_percentage": 5.26,
                "total_goals": 3,
                "completed_goals": 1,
                "active_accounts": 2,
                "last_activity": "2026-02-01T10:30:00Z"
            }
        }
    )
