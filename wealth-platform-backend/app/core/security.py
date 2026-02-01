"""
Security Module
===============

Provides security utilities for the wealth platform:
- JWT token creation and verification
- Password hashing with bcrypt
- API key generation
- Field-level encryption for PII
- HMAC signature generation
- Rate limiting helpers
"""

import base64
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
)

# =============================================================================
# Password Hashing
# =============================================================================

# Bcrypt context with 12 rounds (recommended for bank-grade security)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, ""


# =============================================================================
# JWT Token Management
# =============================================================================

def create_access_token(
    subject: Union[str, int],
    additional_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        additional_claims: Extra claims to include in token
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, int],
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        subject: Token subject (usually user ID)
        additional_claims: Extra claims to include in token
        
    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_token_pair(
    subject: Union[str, int],
    additional_claims: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Create an access and refresh token pair.
    
    Args:
        subject: Token subject (usually user ID)
        additional_claims: Extra claims to include in tokens
        
    Returns:
        Dictionary with 'access_token' and 'refresh_token' keys
    """
    return {
        "access_token": create_access_token(subject, additional_claims),
        "refresh_token": create_refresh_token(subject, additional_claims),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        token_type: Expected token type ('access' or 'refresh')
        
    Returns:
        Decoded token payload
        
    Raises:
        TokenExpiredError: If token has expired
        InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            raise InvalidTokenError(f"Expected {token_type} token")
        
        return payload
        
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError as e:
        raise InvalidTokenError(str(e))


def get_token_subject(token: str) -> str:
    """
    Extract subject from token without full verification.
    Useful for logging and debugging.
    
    Args:
        token: JWT token string
        
    Returns:
        Token subject (user ID)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}
        )
        return payload.get("sub", "")
    except JWTError:
        return ""


# =============================================================================
# API Key Management
# =============================================================================

def generate_api_key(prefix: str = "pk") -> Tuple[str, str]:
    """
    Generate a secure API key for bank partners.
    
    Args:
        prefix: Key prefix ('pk' for publishable, 'sk' for secret)
        
    Returns:
        Tuple of (api_key, hashed_key)
        Store hashed_key in database, return api_key to user once.
    """
    # Generate 32 bytes of random data
    random_bytes = secrets.token_bytes(32)
    
    # Create key with prefix and base64 encoding
    key_body = base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
    api_key = f"{prefix}_{settings.ENVIRONMENT[:4]}_{key_body}"
    
    # Hash the key for storage
    hashed_key = hash_api_key(api_key)
    
    return api_key, hashed_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        api_key: Plain API key
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(
        (api_key + settings.API_KEY_SALT).encode()
    ).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        api_key: Plain API key to verify
        hashed_key: Stored hashed key
        
    Returns:
        True if key matches, False otherwise
    """
    return secrets.compare_digest(hash_api_key(api_key), hashed_key)


# =============================================================================
# Field-Level Encryption (for PII)
# =============================================================================

def _get_fernet_key() -> bytes:
    """
    Derive a Fernet key from the encryption key setting.
    
    Returns:
        Fernet-compatible key bytes
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.API_KEY_SALT.encode()[:16],
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(
        kdf.derive(settings.ENCRYPTION_KEY.encode())
    )
    return key


def encrypt_pii(plaintext: str) -> str:
    """
    Encrypt PII data using AES-256 (via Fernet).
    
    Use for:
    - Emirates ID
    - Iqama numbers
    - Tax identification numbers
    - Bank account numbers
    
    Args:
        plaintext: Data to encrypt
        
    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""
    
    fernet = Fernet(_get_fernet_key())
    encrypted = fernet.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_pii(ciphertext: str) -> str:
    """
    Decrypt PII data.
    
    Args:
        ciphertext: Base64-encoded encrypted string
        
    Returns:
        Decrypted plaintext
        
    Raises:
        AuthenticationError: If decryption fails
    """
    if not ciphertext:
        return ""
    
    try:
        fernet = Fernet(_get_fernet_key())
        decrypted = fernet.decrypt(
            base64.urlsafe_b64decode(ciphertext.encode())
        )
        return decrypted.decode()
    except InvalidToken:
        raise AuthenticationError("Failed to decrypt data - invalid key or corrupted data")


# =============================================================================
# HMAC Signature Generation
# =============================================================================

def generate_hmac_signature(
    payload: str,
    secret: Optional[str] = None
) -> str:
    """
    Generate HMAC-SHA256 signature for API callbacks.
    
    Args:
        payload: String payload to sign
        secret: Optional secret key (uses SECRET_KEY if not provided)
        
    Returns:
        Hex-encoded HMAC signature
    """
    key = (secret or settings.SECRET_KEY).encode()
    signature = hmac.new(key, payload.encode(), hashlib.sha256)
    return signature.hexdigest()


def verify_hmac_signature(
    payload: str,
    signature: str,
    secret: Optional[str] = None
) -> bool:
    """
    Verify HMAC-SHA256 signature.
    
    Args:
        payload: Original payload
        signature: Signature to verify
        secret: Secret key used for signing
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected = generate_hmac_signature(payload, secret)
    return secrets.compare_digest(expected, signature)


# =============================================================================
# Utility Functions
# =============================================================================

def generate_random_string(length: int = 32, include_special: bool = False) -> str:
    """
    Generate a cryptographically secure random string.
    
    Args:
        length: Length of string to generate
        include_special: Include special characters
        
    Returns:
        Random string
    """
    alphabet = string.ascii_letters + string.digits
    if include_special:
        alphabet += "!@#$%^&*"
    
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code (for email/SMS verification).
    
    Args:
        length: Length of code (default 6)
        
    Returns:
        Numeric string code
    """
    return "".join(secrets.choice(string.digits) for _ in range(length))


def mask_email(email: str) -> str:
    """
    Mask an email address for display.
    
    Example:
        john.doe@company.com -> j***e@c***.com
        
    Args:
        email: Email address to mask
        
    Returns:
        Masked email address
    """
    if not email or "@" not in email:
        return email
    
    local, domain = email.split("@")
    domain_parts = domain.split(".")
    
    # Mask local part
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    
    # Mask domain
    if len(domain_parts[0]) <= 2:
        masked_domain = domain_parts[0][0] + "***"
    else:
        masked_domain = domain_parts[0][0] + "***"
    
    return f"{masked_local}@{masked_domain}.{domain_parts[-1]}"


def mask_phone(phone: str) -> str:
    """
    Mask a phone number for display.
    
    Example:
        +971501234567 -> +971****4567
        
    Args:
        phone: Phone number to mask
        
    Returns:
        Masked phone number
    """
    if not phone or len(phone) < 8:
        return phone
    
    # Keep first 4 and last 4 characters
    return phone[:4] + "****" + phone[-4:]
