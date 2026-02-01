"""
Application Configuration
=========================

Pydantic BaseSettings for environment-based configuration.
Validates all config values and provides type-safe access.
"""

from functools import lru_cache
from typing import Any, List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Supports:
    - .env file loading
    - Environment variable override
    - Default values for development
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # =========================================================================
    # Application Settings
    # =========================================================================
    APP_NAME: str = Field(default="WealthPlatform", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v.lower()
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")
        return v.upper()
    
    # =========================================================================
    # Database Configuration
    # =========================================================================
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://wealth_user:wealth_pass@localhost:5432/wealth_platform",
        description="Async PostgreSQL connection URL"
    )
    DATABASE_SYNC_URL: str = Field(
        default="postgresql://wealth_user:wealth_pass@localhost:5432/wealth_platform",
        description="Sync PostgreSQL connection URL (for Alembic)"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, ge=5, le=100, description="Connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50, description="Max pool overflow")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    @property
    def database_settings(self) -> dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "echo": self.DATABASE_ECHO,
            "pool_pre_ping": True,  # Check connection health
            "pool_recycle": 3600,   # Recycle connections every hour
        }
    
    # =========================================================================
    # Redis Configuration
    # =========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, ge=0, le=15, description="Redis database number")
    REDIS_CACHE_TTL: int = Field(default=300, ge=60, description="Default cache TTL in seconds")
    
    # =========================================================================
    # Security Configuration
    # =========================================================================
    SECRET_KEY: str = Field(
        default="development-secret-key-change-in-production-min-32-chars",
        min_length=32,
        description="JWT secret key"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, ge=5, le=60, description="Access token expiry (minutes)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, ge=1, le=30, description="Refresh token expiry (days)"
    )
    ENCRYPTION_KEY: str = Field(
        default="development-encryption-key-32-bytes!",
        min_length=32,
        description="AES-256 encryption key for PII"
    )
    API_KEY_SALT: str = Field(
        default="unique-salt-for-api-key-generation",
        description="Salt for API key generation"
    )
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        # In production, ensure not using default
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and "development" in v.lower():
            raise ValueError("Must set a secure SECRET_KEY in production")
        return v
    
    # =========================================================================
    # AWS Configuration
    # =========================================================================
    AWS_REGION: str = Field(default="me-south-1", description="AWS region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret key")
    S3_BUCKET_NAME: str = Field(default="wealth-platform-docs", description="S3 bucket name")
    S3_BUCKET_REGION: str = Field(default="me-south-1", description="S3 bucket region")
    
    @property
    def aws_configured(self) -> bool:
        """Check if AWS is properly configured."""
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)
    
    # =========================================================================
    # CORS Configuration
    # =========================================================================
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:8080",
        description="Comma-separated list of allowed CORS origins"
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """Get list of CORS origins."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # =========================================================================
    # Multi-Tenancy Configuration
    # =========================================================================
    DEFAULT_TENANT: str = Field(default="system", description="Default tenant identifier")
    TENANT_HEADER: str = Field(default="X-Bank-Tenant", description="HTTP header for tenant ID")
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    RATE_LIMIT_REQUESTS: int = Field(
        default=100, ge=10, description="Max requests per window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60, ge=10, description="Rate limit window in seconds"
    )
    
    # =========================================================================
    # Mock APIs Configuration
    # =========================================================================
    MOCK_APIS_ENABLED: bool = Field(default=True, description="Enable mock bank APIs")
    MOCK_API_DELAY_MS: int = Field(default=150, ge=0, le=1000, description="Mock API delay (ms)")
    
    # =========================================================================
    # Email Configuration
    # =========================================================================
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="noreply@wealthplatform.ae", description="From email")
    SMTP_FROM_NAME: str = Field(default="Wealth Platform", description="From name")
    
    @property
    def email_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASSWORD)
    
    # =========================================================================
    # Stripe Configuration
    # =========================================================================
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, description="Stripe secret key")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, description="Stripe publishable key")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Stripe webhook secret")
    
    @property
    def stripe_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.STRIPE_SECRET_KEY)
    
    # =========================================================================
    # Celery Configuration
    # =========================================================================
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to avoid re-reading environment on every access.
    """
    return Settings()


# Global settings instance
settings = get_settings()
