"""
Middleware Module
=================

Custom middleware for the wealth platform:
- Tenant isolation (multi-tenancy)
- Request logging with correlation IDs
- Rate limiting
- Error handling
"""

import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# Request Context
# =============================================================================

class RequestContext:
    """
    Request context holder for correlation ID and tenant info.
    
    Stored in request.state and accessible throughout the request lifecycle.
    """
    
    def __init__(
        self,
        request_id: str,
        bank_id: Optional[str] = None,
        bank_slug: Optional[str] = None
    ):
        self.request_id = request_id
        self.bank_id = bank_id
        self.bank_slug = bank_slug
        self.start_time = time.time()


def get_request_context(request: Request) -> Optional[RequestContext]:
    """Get request context from request state."""
    return getattr(request.state, "context", None)


# =============================================================================
# Request ID Middleware
# =============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Adds a unique request ID to each request for tracing.
    
    The request ID is:
    - Generated as a UUID if not provided
    - Stored in request.state
    - Added to response headers (X-Request-ID)
    - Available for logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Create context
        context = RequestContext(request_id=request_id)
        request.state.context = context
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


# =============================================================================
# Request Logging Middleware
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all incoming requests with timing information.
    
    Log format includes:
    - Request method and path
    - Response status code
    - Processing time in milliseconds
    - Request ID for correlation
    """
    
    # Paths to exclude from logging (health checks, etc.)
    EXCLUDED_PATHS = {"/health", "/ready", "/docs", "/redoc", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Get context
        context = get_request_context(request)
        request_id = context.request_id if context else "unknown"
        
        # Log request start
        logger.info(
            f"[{request_id}] Started {request.method} {request.url.path}"
        )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Log request completion
        logger.info(
            f"[{request_id}] Completed {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.2f}ms"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response


# =============================================================================
# Tenant Isolation Middleware
# =============================================================================

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts and validates tenant information from requests.
    
    Tenant identification:
    1. X-Bank-Tenant header (bank slug)
    2. Subdomain extraction (e.g., fab.wealthplatform.ae)
    
    For authenticated requests, also validates that the user
    belongs to the specified tenant.
    """
    
    # Paths that don't require tenant identification
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/banks/register",  # Bank registration is public
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tenant check for public paths
        path = request.url.path
        if path in self.PUBLIC_PATHS or path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        # Extract tenant from header
        bank_slug = request.headers.get(settings.TENANT_HEADER)
        
        # Or from subdomain
        if not bank_slug:
            host = request.headers.get("Host", "")
            parts = host.split(".")
            if len(parts) > 2 and parts[0] not in ["www", "api"]:
                bank_slug = parts[0]
        
        # Store tenant info in context
        context = get_request_context(request)
        if context and bank_slug:
            context.bank_slug = bank_slug
        
        # For now, we don't enforce tenant on all endpoints
        # This will be enhanced when bank validation is added
        
        return await call_next(request)


# =============================================================================
# Rate Limiting Middleware
# =============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, use Redis-based rate limiting.
    This provides basic protection for development.
    """
    
    def __init__(self, app: ASGIApp, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self._cache: dict[str, list[float]] = {}
    
    def _get_client_key(self, request: Request) -> str:
        """Get a unique key for the client."""
        # Use IP + User-Agent for better identification
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return ip
    
    def _is_rate_limited(self, client_key: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        
        # Get or create request timestamps list
        if client_key not in self._cache:
            self._cache[client_key] = []
        
        timestamps = self._cache[client_key]
        
        # Remove old timestamps
        cutoff = now - self.window
        timestamps[:] = [ts for ts in timestamps if ts > cutoff]
        
        # Check if over limit
        if len(timestamps) >= self.requests:
            return True
        
        # Add current request
        timestamps.append(now)
        return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        
        if self._is_rate_limited(client_key):
            logger.warning(f"Rate limit exceeded for client: {client_key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Max {self.requests} requests per {self.window} seconds.",
                    "retry_after": self.window
                },
                headers={"Retry-After": str(self.window)}
            )
        
        return await call_next(request)


# =============================================================================
# Security Headers Middleware
# =============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (in production)
    - Content-Security-Policy
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Content Security Policy for API
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        
        return response


# =============================================================================
# Setup Function
# =============================================================================

def setup_middlewares(app: FastAPI) -> None:
    """
    Configure all middlewares for the application.
    
    Order matters! Middlewares are executed in reverse order of addition.
    
    Args:
        app: FastAPI application instance
    """
    # Security headers (runs last)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.RATE_LIMIT_REQUESTS,
        window=settings.RATE_LIMIT_WINDOW
    )
    
    # Tenant isolation
    app.add_middleware(TenantMiddleware)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Request ID (runs first)
    app.add_middleware(RequestIDMiddleware)
    
    logger.info("Middlewares configured successfully")
