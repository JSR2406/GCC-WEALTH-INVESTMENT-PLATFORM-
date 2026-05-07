<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1117,50:1a1f35,100:FFD700&height=160&section=header&text=GCC%20Wealth%20Platform&fontSize=36&fontColor=FFD700&fontAlignY=45&animation=fadeIn"/>

# 💰 GCC Wealth Investment Platform

**A full-stack AI-powered wealth management and investment platform tailored for the GCC (Gulf Cooperation Council) market — with real-time portfolio analytics, smart investment recommendations, and a modern financial dashboard.**

[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

🔗 **[Live Demo](https://wealth-platform-user-app.vercel.app)**

</div>

---

## 🧠 Overview

The **GCC Wealth Investment Platform** is a production-ready FinTech application designed for investors across the Gulf Cooperation Council region. It combines real-time market data, AI-driven portfolio optimization, and an intuitive financial dashboard to deliver a comprehensive wealth management experience.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Portfolio Dashboard** | Real-time holdings, P&L tracking, and sector allocation |
| 🤖 **AI Recommendations** | Smart investment suggestions based on risk profile |
| 📈 **Market Data** | Live prices for GCC stocks, ETFs, crypto, commodities |
| 🔐 **Risk Assessment** | AI-powered risk profiling and portfolio scoring |
| 🏆 **GCC Markets** | Saudi Tadawul, UAE DFM/ADX, Kuwait, Qatar stock exchanges |
| 💳 **Stripe Payments** | Subscription management with Stripe integration |
| 📊 **Analytics Reports** | Downloadable portfolio performance reports |

---

## 🛠️ Tech Stack

### Backend (`wealth-platform-backend/`)
| Technology | Purpose |
|------------|---------|
| **Python / FastAPI** | REST API & business logic |
| **PostgreSQL** | User & portfolio data |
| **Stripe** | Payment processing |
| **Docker** | Containerized deployment |
| **AI/ML Models** | Investment recommendations |

### Frontend (`wealth-platform-user-app/`)
| Technology | Purpose |
|------------|---------|
| **Next.js / TypeScript** | Full-stack React framework |
| **Tailwind CSS** | Responsive modern styling |
| **Recharts** | Financial data visualization |
| **Vercel** | Deployment platform |

---

## 📁 Project Structure

```
GCC-WEALTH-INVESTMENT-PLATFORM-/
├── wealth-platform-backend/    # FastAPI Python backend
│   ├── api/                    # Route handlers
│   ├── models/                 # Data models & schemas
│   ├── services/               # Business logic
│   ├── docker-compose.yml      # Docker setup
│   └── requirements.txt
└── wealth-platform-user-app/   # Next.js frontend
    ├── app/                    # App Router pages
    ├── components/             # UI components
    ├── lib/                    # API client & utilities
    └── package.json
```

---

## 🚀 Getting Started

### Backend
```bash
cd wealth-platform-backend
docker-compose up --build
# API runs on http://localhost:8000
```

### Frontend
```bash
cd wealth-platform-user-app
npm install
npm run dev
# App runs on http://localhost:3000
```

---

## 🌍 GCC Markets Supported

- 🇸🇦 Saudi Arabia — Tadawul (Saudi Exchange)
- 🇦🇪 UAE — DFM (Dubai) & ADX (Abu Dhabi)
- 🇰🇼 Kuwait — Boursa Kuwait
- 🇶🇦 Qatar — Qatar Stock Exchange
- 🇧🇭 Bahrain — Bahrain Bourse

---

## 👨‍💻 Author

**Janmejay Singh Rathore**
- 🐙 GitHub: [@JSR2406](https://github.com/JSR2406)
- 💼 LinkedIn: [janmejay-singh-rathore](https://linkedin.com/in/janmejay-singh-rathore)
- 📧 Email: janmejaysingh2406@gmail.com

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FFD700,100:0D1117&height=100&section=footer"/>
</div>
