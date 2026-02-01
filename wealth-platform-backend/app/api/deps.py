"""
API Dependencies
================

FastAPI dependency injection for:
- Database sessions
- Authentication
- Authorization (RBAC)
- Pagination
- Tenant context
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    TenantAccessDeniedError,
)
from app.core.security import verify_token

# =============================================================================
# Security Schemes
# =============================================================================

oauth2_scheme = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Enter your access token",
    auto_error=False
)


# =============================================================================
# Pagination Parameters
# =============================================================================

class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


Pagination = Annotated[PaginationParams, Depends()]


# =============================================================================
# Database Dependency
# =============================================================================

Database = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# Tenant Dependencies
# =============================================================================

async def get_tenant_slug(
    x_bank_tenant: Optional[str] = Header(None, alias=settings.TENANT_HEADER)
) -> Optional[str]:
    """
    Extract tenant slug from request header.
    
    Returns:
        Bank slug or None
    """
    return x_bank_tenant


TenantSlug = Annotated[Optional[str], Depends(get_tenant_slug)]


async def require_tenant(
    tenant_slug: TenantSlug
) -> str:
    """
    Require tenant identification.
    
    Raises:
        HTTPException: If tenant header is missing
    """
    if not tenant_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TENANT_REQUIRED",
                "message": f"Missing required header: {settings.TENANT_HEADER}"
            }
        )
    return tenant_slug


RequiredTenant = Annotated[str, Depends(require_tenant)]


# =============================================================================
# Authentication Dependencies
# =============================================================================

async def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)
) -> Optional[dict]:
    """
    Extract and verify JWT token from Authorization header.
    
    Returns:
        Token payload or None if no token provided
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials, token_type="access")
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


CurrentToken = Annotated[Optional[dict], Depends(get_current_token)]


async def require_auth(
    token: CurrentToken
) -> dict:
    """
    Require valid authentication token.
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": "Authentication required"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    return token


RequiredAuth = Annotated[dict, Depends(require_auth)]


# =============================================================================
# User Context
# =============================================================================

class CurrentUser:
    """Current authenticated user context."""
    
    def __init__(
        self,
        user_id: str,
        bank_id: str,
        email: str,
        role: str,
        permissions: list[str]
    ):
        self.user_id = UUID(user_id)
        self.bank_id = UUID(bank_id)
        self.email = email
        self.role = role
        self.permissions = permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or "admin" in self.permissions
    
    def is_bank_admin(self) -> bool:
        """Check if user is a bank admin."""
        return self.role in ["bank_admin", "bank_super_admin"]
    
    def is_platform_admin(self) -> bool:
        """Check if user is a platform admin."""
        return self.role == "platform_admin"


async def get_current_user(
    token: RequiredAuth,
    db: Database
) -> CurrentUser:
    """
    Get current authenticated user from token.
    
    Returns:
        CurrentUser object with user details
    """
    # Extract user info from token
    user_id = token.get("sub")
    bank_id = token.get("bank_id")
    email = token.get("email", "")
    role = token.get("role", "user")
    permissions = token.get("permissions", [])
    
    if not user_id or not bank_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN_CLAIMS",
                "message": "Token missing required claims"
            }
        )
    
    # TODO: Optionally verify user still exists in database
    # user = await get_or_none(db, User, id=user_id, is_active=True)
    # if not user:
    #     raise HTTPException(status_code=401, detail="User not found")
    
    return CurrentUser(
        user_id=user_id,
        bank_id=bank_id,
        email=email,
        role=role,
        permissions=permissions
    )


AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]


# =============================================================================
# Authorization Dependencies
# =============================================================================

def require_permissions(*required_permissions: str):
    """
    Factory for permission-checking dependency.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_permissions("admin"))])
    """
    async def check_permissions(user: AuthenticatedUser):
        for permission in required_permissions:
            if not user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "PERMISSION_DENIED",
                        "message": f"Required permission: {permission}"
                    }
                )
        return user
    
    return check_permissions


def require_role(*allowed_roles: str):
    """
    Factory for role-checking dependency.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("bank_admin"))])
    """
    async def check_role(user: AuthenticatedUser):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ROLE_REQUIRED",
                    "message": f"Required role: {', '.join(allowed_roles)}"
                }
            )
        return user
    
    return check_role


async def require_bank_admin(user: AuthenticatedUser) -> CurrentUser:
    """Require user to be a bank admin."""
    if not user.is_bank_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "BANK_ADMIN_REQUIRED",
                "message": "Bank administrator access required"
            }
        )
    return user


async def require_platform_admin(user: AuthenticatedUser) -> CurrentUser:
    """Require user to be a platform admin."""
    if not user.is_platform_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PLATFORM_ADMIN_REQUIRED",
                "message": "Platform administrator access required"
            }
        )
    return user


BankAdmin = Annotated[CurrentUser, Depends(require_bank_admin)]
PlatformAdmin = Annotated[CurrentUser, Depends(require_platform_admin)]


# =============================================================================
# Bank Resource Access
# =============================================================================

async def verify_bank_access(
    bank_id: UUID,
    user: AuthenticatedUser
) -> UUID:
    """
    Verify user has access to specified bank.
    
    Args:
        bank_id: Bank ID to access
        user: Current authenticated user
        
    Returns:
        The bank_id if access is granted
        
    Raises:
        TenantAccessDeniedError: If user doesn't belong to the bank
    """
    # Platform admins can access any bank
    if user.is_platform_admin():
        return bank_id
    
    # Users can only access their own bank
    if user.bank_id != bank_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "BANK_ACCESS_DENIED",
                "message": "You don't have access to this bank's resources"
            }
        )
    
    return bank_id
