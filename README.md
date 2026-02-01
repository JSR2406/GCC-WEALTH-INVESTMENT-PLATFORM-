# GCC Wealth Platform

## 🚀 Final Demo & Quick Start

The platform is fully integrated with a FastAPI Backend (Python) and a Next.js Frontend (TypeScript).

### 🔗 **Demo Link:** [http://localhost:3000](http://localhost:3000)

---

### 1️⃣ Start the Backend (API & Database)

The backend runs on port `8000` and manages the PostgreSQL database and Stripe integration.

**Using Docker (Recommended):**
```bash
cd wealth-platform-backend
docker-compose up --build
```

**Manual Setup (Alternative):**
```bash
cd wealth-platform-backend
# Install dependencies
pip install -r requirements.txt
# Run migrations
alembic upgrade head
# Seed data
python -m scripts.seed_fee_configs
# Start server
uvicorn app.main:app --reload
```

### 2️⃣ Start the Frontend (User App)

The frontend runs on port `3000` and acts as the user interface.

```bash
cd wealth-platform-user-app
# Install dependencies (if not done)
npm install
# Start development server
npm run dev
```

---

### ✨ Key Features to Test

1.  **Dashboard**: View portfolio summary and real-time status.
2.  **Service Fees**: Go to the "Fees" section or try to generate a Tax Report to see the fee disclosure.
    *   *Note: Ensure `STRIPE_SECRET_KEY` is set in `.env` for actual payments, or it will run in mock mode.*
3.  **Bank Integration**: Switch between banks (FAB, HSBC, Al Rajhi) using the tenant selector.
