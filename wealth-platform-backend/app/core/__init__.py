"""
Core Module
===========

Contains core functionality:
- config: Application settings (Pydantic BaseSettings)
- security: JWT, encryption, password hashing
- database: SQLAlchemy async engine and sessions
- middleware: Tenant isolation, CORS, logging
- exceptions: Custom exception classes
"""

from app.core.config import settings

__all__ = ["settings"]
