"""
Common Schemas
==============

Shared Pydantic schemas used across the application.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# =============================================================================
# Response Wrappers
# =============================================================================

class SuccessResponse(BaseModel):
    """Standard success response wrapper."""
    
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation successful",
                "data": {}
            }
        }
    )


class ErrorDetail(BaseModel):
    """Error detail structure."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    
    success: bool = False
    error: ErrorDetail
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input",
                    "details": {"field": "email", "message": "Invalid email format"}
                }
            }
        }
    )


# =============================================================================
# Pagination
# =============================================================================

class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_prev: bool = Field(..., description="Whether there's a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    success: bool = True
    data: List[T]
    pagination: PaginationMeta
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }
    )


# =============================================================================
# Health Check
# =============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")


class ReadinessCheckResponse(BaseModel):
    """Readiness check response."""
    
    status: str = Field(..., description="Readiness status")
    checks: dict[str, str] = Field(..., description="Dependency health checks")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")


# =============================================================================
# Authentication
# =============================================================================

class TokenPair(BaseModel):
    """JWT token pair response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    
    refresh_token: str = Field(..., description="Current refresh token")


# =============================================================================
# Base Model Mixins
# =============================================================================

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class UUIDMixin(BaseModel):
    """Mixin for UUID primary key."""
    
    id: UUID = Field(..., description="Unique identifier")


# =============================================================================
# Currency & Money
# =============================================================================

class MoneyAmount(BaseModel):
    """Money amount with currency."""
    
    amount: float = Field(..., ge=0, description="Amount value")
    currency: str = Field(default="USD", max_length=3, description="ISO 4217 currency code")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 25000.00,
                "currency": "USD"
            }
        }
    )


# =============================================================================
# Date/Period
# =============================================================================

class DateRange(BaseModel):
    """Date range for filtering."""
    
    start_date: datetime = Field(..., description="Start date (inclusive)")
    end_date: datetime = Field(..., description="End date (inclusive)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z"
            }
        }
    )


class MonthPeriod(BaseModel):
    """Month period specification."""
    
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2100, description="Year")
    
    @property
    def period_string(self) -> str:
        """Get YYYY-MM string."""
        return f"{self.year}-{self.month:02d}"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "month": 2,
                "year": 2026
            }
        }
    )
