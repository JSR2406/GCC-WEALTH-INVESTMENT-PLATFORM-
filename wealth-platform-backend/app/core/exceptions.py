"""
Custom Exceptions
=================

Centralized exception definitions for the wealth platform.
Provides consistent error handling across the application.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class WealthPlatformException(Exception):
    """Base exception for the wealth platform."""
    
    def __init__(
        self,
        message: str,
        code: str = "PLATFORM_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


# =============================================================================
# Authentication & Authorization Exceptions
# =============================================================================

class AuthenticationError(WealthPlatformException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(WealthPlatformException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict] = None):
        super().__init__(message, code="AUTHORIZATION_ERROR", details=details)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, details={"expired": True})


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are incorrect."""
    
    def __init__(self):
        super().__init__("Invalid email or password")


# =============================================================================
# Bank Exceptions
# =============================================================================

class BankError(WealthPlatformException):
    """Base exception for bank-related errors."""
    pass


class BankNotFoundError(BankError):
    """Raised when bank is not found."""
    
    def __init__(self, bank_id: Optional[str] = None, slug: Optional[str] = None):
        identifier = bank_id or slug or "unknown"
        super().__init__(
            f"Bank not found: {identifier}",
            code="BANK_NOT_FOUND",
            details={"bank_id": bank_id, "slug": slug}
        )


class BankSlugTakenError(BankError):
    """Raised when bank slug is already in use."""
    
    def __init__(self, slug: str):
        super().__init__(
            f"Bank slug '{slug}' is already taken",
            code="BANK_SLUG_TAKEN",
            details={"slug": slug}
        )


class BankSuspendedError(BankError):
    """Raised when trying to access a suspended bank."""
    
    def __init__(self, bank_id: str):
        super().__init__(
            "Bank account is suspended",
            code="BANK_SUSPENDED",
            details={"bank_id": bank_id}
        )


class InvalidRevenueModelError(BankError):
    """Raised when revenue model configuration is invalid."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, code="INVALID_REVENUE_MODEL", details=details)


# =============================================================================
# User Exceptions
# =============================================================================

class UserError(WealthPlatformException):
    """Base exception for user-related errors."""
    pass


class UserNotFoundError(UserError):
    """Raised when user is not found."""
    
    def __init__(self, user_id: Optional[str] = None, email: Optional[str] = None):
        identifier = user_id or email or "unknown"
        super().__init__(
            f"User not found: {identifier}",
            code="USER_NOT_FOUND",
            details={"user_id": user_id, "email": email}
        )


class UserAlreadyExistsError(UserError):
    """Raised when trying to create duplicate user."""
    
    def __init__(self, email: str, bank_id: str):
        super().__init__(
            f"User with email '{email}' already exists for this bank",
            code="USER_EXISTS",
            details={"email": email, "bank_id": bank_id}
        )


class UserInactiveError(UserError):
    """Raised when inactive user tries to access platform."""
    
    def __init__(self, user_id: str):
        super().__init__(
            "User account is inactive",
            code="USER_INACTIVE",
            details={"user_id": user_id}
        )


class KYCNotVerifiedError(UserError):
    """Raised when user KYC is not verified."""
    
    def __init__(self, user_id: str, kyc_status: str):
        super().__init__(
            "KYC verification required",
            code="KYC_NOT_VERIFIED",
            details={"user_id": user_id, "kyc_status": kyc_status}
        )


# =============================================================================
# Tenant Exceptions
# =============================================================================

class TenantError(WealthPlatformException):
    """Base exception for multi-tenancy errors."""
    pass


class TenantNotFoundError(TenantError):
    """Raised when tenant is not found."""
    
    def __init__(self, tenant_id: str):
        super().__init__(
            f"Tenant not found: {tenant_id}",
            code="TENANT_NOT_FOUND",
            details={"tenant_id": tenant_id}
        )


class TenantAccessDeniedError(TenantError):
    """Raised when accessing data from another tenant."""
    
    def __init__(self, resource: str, tenant_id: str):
        super().__init__(
            f"Access denied to resource from tenant: {tenant_id}",
            code="TENANT_ACCESS_DENIED",
            details={"resource": resource, "tenant_id": tenant_id}
        )


# =============================================================================
# Revenue Exceptions
# =============================================================================

class RevenueError(WealthPlatformException):
    """Base exception for revenue calculation errors."""
    pass


class RevenueCalculationError(RevenueError):
    """Raised when revenue calculation fails."""
    
    def __init__(self, message: str, bank_id: str, period: str):
        super().__init__(
            message,
            code="REVENUE_CALCULATION_ERROR",
            details={"bank_id": bank_id, "period": period}
        )


class DuplicateInvoiceError(RevenueError):
    """Raised when invoice already exists for period."""
    
    def __init__(self, bank_id: str, period: str):
        super().__init__(
            f"Invoice already exists for period: {period}",
            code="DUPLICATE_INVOICE",
            details={"bank_id": bank_id, "period": period}
        )


# =============================================================================
# Database Exceptions
# =============================================================================

class DatabaseError(WealthPlatformException):
    """Base exception for database errors."""
    
    def __init__(self, message: str = "Database error occurred", details: Optional[Dict] = None):
        super().__init__(message, code="DATABASE_ERROR", details=details)


class TransactionError(DatabaseError):
    """Raised when database transaction fails."""
    
    def __init__(self, operation: str):
        super().__init__(
            f"Transaction failed: {operation}",
            details={"operation": operation}
        )


# =============================================================================
# External Service Exceptions
# =============================================================================

class ExternalServiceError(WealthPlatformException):
    """Base exception for external service errors."""
    pass


class BankAPIError(ExternalServiceError):
    """Raised when bank API call fails."""
    
    def __init__(self, bank_slug: str, endpoint: str, status_code: Optional[int] = None):
        super().__init__(
            f"Bank API error: {bank_slug}",
            code="BANK_API_ERROR",
            details={"bank_slug": bank_slug, "endpoint": endpoint, "status_code": status_code}
        )


class S3UploadError(ExternalServiceError):
    """Raised when S3 upload fails."""
    
    def __init__(self, bucket: str, key: str, error: str):
        super().__init__(
            f"S3 upload failed: {error}",
            code="S3_UPLOAD_ERROR",
            details={"bucket": bucket, "key": key}
        )


class EmailDeliveryError(ExternalServiceError):
    """Raised when email delivery fails."""
    
    def __init__(self, recipient: str, error: str):
        super().__init__(
            f"Email delivery failed: {error}",
            code="EMAIL_DELIVERY_ERROR",
            details={"recipient": recipient}
        )


# =============================================================================
# Validation Exceptions
# =============================================================================

class ValidationError(WealthPlatformException):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str, value: Optional[Any] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": value}
        )


class InvalidCurrencyError(ValidationError):
    """Raised when currency code is invalid."""
    
    def __init__(self, currency: str):
        super().__init__(
            field="currency",
            message=f"Invalid currency code: {currency}",
            value=currency
        )


class InvalidCountryError(ValidationError):
    """Raised when country code is invalid."""
    
    def __init__(self, country: str):
        super().__init__(
            field="country",
            message=f"Invalid country code: {country}. Must be 'AE' or 'SA'",
            value=country
        )


# =============================================================================
# Rate Limiting Exceptions
# =============================================================================

class RateLimitExceededError(WealthPlatformException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, limit: int, window: int, retry_after: int):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window} seconds",
            code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window, "retry_after": retry_after}
        )


# =============================================================================
# HTTP Exception Factory
# =============================================================================

def create_http_exception(
    exc: WealthPlatformException,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> HTTPException:
    """
    Convert WealthPlatformException to FastAPI HTTPException.
    
    Args:
        exc: The platform exception to convert
        status_code: HTTP status code to use
        
    Returns:
        HTTPException with structured detail
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


# Exception to HTTP status code mapping
EXCEPTION_STATUS_MAP = {
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    BankNotFoundError: status.HTTP_404_NOT_FOUND,
    BankSlugTakenError: status.HTTP_409_CONFLICT,
    BankSuspendedError: status.HTTP_403_FORBIDDEN,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    TenantNotFoundError: status.HTTP_404_NOT_FOUND,
    TenantAccessDeniedError: status.HTTP_403_FORBIDDEN,
    RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}
