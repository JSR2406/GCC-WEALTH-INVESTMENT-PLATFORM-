# GCC WealthTech

A wealth management prototype for GCC banks and their customers. The Next.js app presents bank-branded onboarding, portfolio, and investing-goal workflows. The FastAPI service and the app's demo routes let developers explore the workflows using sample data.

## What to review

- **Bank-branded views** — Open the bank selector or visit `/fab`, `/hsbc`, or `/rajhi` to see the sample tenant experiences.
- **Portfolio and goals** — Browse sample accounts and portfolio summaries, then explore the goal setup and progress views.
- **Onboarding and reporting** — Explore the KYC, documents, and tax views, including sample FATCA, CRS, and Zakat workflows.

## Repository layout

| Path | Responsibility |
| --- | --- |
| [wealth-platform-user-app](wealth-platform-user-app) | Next.js App Router frontend, tenant themes, and demo API routes |
| [Tenant routes](wealth-platform-user-app/src/app/%5Btenant%5D) | Portfolio, goals, onboarding, and tax screens |
| [Frontend API client](wealth-platform-user-app/src/lib/api-client.ts) | API origin configuration and mock fallbacks |
| [wealth-platform-backend](wealth-platform-backend) | FastAPI service, SQLAlchemy models, and PostgreSQL configuration |
| [API entry point](wealth-platform-backend/app/main.py) | FastAPI setup and demo authentication endpoints |
| [Backend tests](wealth-platform-backend/tests) | Pytest suite, including bank endpoint tests |

## Run locally

Use Node.js and npm, and Docker with Compose for the backend's documented container setup. Use development-only settings from the [backend environment example](wealth-platform-backend/.env.example). For the database and migration commands, follow the [backend setup guide](wealth-platform-backend/README.md).

```bash
cd wealth-platform-backend
cp .env.example .env
# Review the example values, then configure local development credentials.
docker compose up --build
```

In a second terminal, from the repository root:

```bash
cd wealth-platform-user-app
npm ci
npm run dev
```

Open `http://localhost:3000`. The browser client defaults to `http://localhost:8000/api/v1`. Set `NEXT_PUBLIC_API_URL` in the frontend environment to use a different development API.

## Demo limits

Use synthetic account data and sample documents. The repository contains mock authentication/data paths and tax screens for demonstration. Live brokerage connectivity, regulatory compliance, and production tenant isolation require independent validation.

[Frontend guide](wealth-platform-user-app/README.md) · [Backend guide](wealth-platform-backend/README.md) · [Janmejay Singh Rathore](https://github.com/JSR2406)
