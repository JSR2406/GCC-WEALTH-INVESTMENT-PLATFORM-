# GCC Wealth Management Platform - Backend

A Cross-Border Wealth Management SaaS Platform for banks in UAE and Saudi Arabia.

## Overview

This platform enables regional banks to offer white-labeled wealth management services to their customers. It supports multiple revenue models (SaaS, Hybrid, AUM Share) and includes features for:

- **Multi-tenant architecture** with bank-level data isolation
- **KYC management** with encrypted PII storage
- **Tax compliance** (FATCA, CRS, Zakat reporting)
- **Revenue calculation & invoicing** based on configurable models
- **Portfolio management** and goal-based investing

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Cache**: Redis
- **Task Queue**: Celery
- **Migrations**: Alembic
- **Auth**: JWT with bcrypt password hashing
- **Encryption**: AES-256 for PII

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Setup with Docker

```bash
# Clone and enter directory
cd wealth-platform-backend

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
wealth-platform-backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── v1/           # Version 1 routes
│   │   │   ├── banks.py  # Bank management
│   │   │   ├── users.py  # User management
│   │   │   ├── revenue.py # Revenue & invoicing
│   │   │   └── portfolios.py # Portfolio & goals
│   │   └── deps.py       # Dependency injection
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings management
│   │   ├── database.py   # Database setup
│   │   ├── security.py   # Auth & encryption
│   │   ├── middleware.py # Custom middleware
│   │   └── exceptions.py # Custom exceptions
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── tests/                # Test suite
├── docker-compose.yml    # Docker services
├── Dockerfile           # Production image
└── requirements.txt     # Dependencies
```

## API Documentation

After starting the server, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Endpoints

### Banks
- `POST /api/v1/banks/register` - Register new bank partner
- `GET /api/v1/banks/{bank_id}` - Get bank details
- `GET /api/v1/banks/{bank_id}/dashboard` - Analytics dashboard
- `PUT /api/v1/banks/{bank_id}/branding` - Update branding

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}/kyc` - Update KYC status
- `PUT /api/v1/users/{user_id}/tax-info` - Update tax info

### Revenue
- `POST /api/v1/revenue/calculate` - Trigger calculation
- `GET /api/v1/revenue/bank/{bank_id}/history` - Revenue history
- `GET /api/v1/revenue/bank/{bank_id}/invoices` - List invoices

### Portfolios
- `GET /api/v1/portfolios/accounts` - List accounts
- `GET /api/v1/portfolios/goals` - List goals
- `POST /api/v1/portfolios/goals` - Create goal

## Revenue Models

| Model | Configuration |
|-------|--------------|
| **SaaS** | Fixed annual fee per user ($10-500/year) |
| **Hybrid** | Base fee + percentage of AUM (1-50%) |
| **AUM Share** | Pure percentage of AUM fees |

## Security

- **Passwords**: bcrypt with 12 rounds
- **JWT Tokens**: HS256 with configurable expiry
- **PII Encryption**: AES-256 (Fernet) for sensitive data
- **API Keys**: Secure generation with hashing

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_banks.py -v
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret for JWT signing
- `ENCRYPTION_KEY` - AES-256 encryption key

## License

Proprietary - All rights reserved.
