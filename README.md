# JatuhTempo — AI-Powered Debt Management Assistant

> **"Preventing Financial Failure, One Debt at a Time."**

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-14-black" alt="Next.js">
  <img src="https://img.shields.io/badge/Telegram%20Bot-Aiogram%203-blue" alt="Telegram Bot">
  <img src="https://img.shields.io/badge/AI-DeepSeek-purple" alt="AI">
  <img src="https://img.shields.io/badge/license-proprietary-red" alt="License">
</p>

---

## 🚀 Overview

JatuhTempo is an intelligent debt management platform built for Indonesia. It combines **AI-powered OCR**, **natural language processing**, **multi-platform bots** (Telegram/Web), and **smart reminders** to help Indonesians track, manage, and eliminate their debt.

Unlike generic debt trackers, JatuhTempo understands the Indonesian financial landscape — paylater platforms (Akulaku, Kredivo, Shopee PayLater), pinjol (online loans), and local installment cultures.

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| **📸 AI OCR** | Screenshot any bill — AI reads it automatically | ✅ Live |
| **🧠 Natural Language Input** | "I owe Kredivo 350k due July 15th" — AI understands | ✅ Live |
| **🤖 Multi-Platform** | Telegram bot + Web dashboard | ✅ Live |
| **🔔 Smart Reminders** | H-7, H-3, H-1, D-Day + overdue notifications | ✅ Live |
| **💰 Payoff Strategy** | Snowball / Avalanche calculator with projections | ✅ Live |
| **📊 Interest Rate Learning** | AI learns platform rates, suggests optimal payoff | ✅ Live |
| **📱 Responsive Design** | Full mobile-first web experience | ✅ Live |
| **🔒 Demo Account** | Try it instantly: `demo@jatuhtempo.app` / `demo123` | ✅ Live |
| **💳 Subscription** | Polar.sh integration for premium features | 🚧 Setup |
| **📅 Calendar Sync** | Due dates in Google Calendar / iCloud / Outlook | 📋 Planned |
| **🧘 Behavioral Nudge** | AI detects patterns, sends personal nudges | 📋 Planned |
| **📞 WhatsApp Bot** | Full parity with Telegram bot via WhatsApp | 📋 Planned |

---

## 🛠 Tech Stack

### Backend
```
Python 3.11+   → FastAPI 0.115
SQLAlchemy     → PostgreSQL 15 (async)
APScheduler    → Reminder system
Redis          → Caching / session mgmt
Alembic        → Database migrations
```

### Frontend
```
Next.js 14     → App Router + Server Components
TypeScript     → Type-safe codebase
Tailwind CSS   → Utility-first styling
```

### Bot
```
Aiogram 3      → Telegram Bot framework (FSM, keyboards, media)
```

### AI
```
DeepSeek API   → NL parsing + OCR text extraction
Tesseract OCR  → Image text extraction pipeline
```

### Infrastructure
```
Docker         → Containerized deployment
Railway        → Cloud hosting (jatuhtempo.up.railway.app)
Polar.sh       → Subscription payment gateway
```

---

## 🚦 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
- **DeepSeek API Key**

### Installation

```bash
# Clone the repository
git clone https://github.com/FMATheNomad/jatuhtempo.git
cd jatuhtempo

# Backend setup
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys

# Run backend
uvicorn app.main:app --reload

# Frontend setup (separate terminal)
cd web
npm install
npm run dev
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ✅ |
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI | ✅ |
| `JWT_SECRET` | JWT signing secret | ✅ |
| `POLAR_WEBHOOK_SECRET` | Polar.sh webhook secret | For payments |
| `REDIS_URL` | Redis connection string | Optional |

See `.env.example` for complete list.

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome + stats dashboard |
| `/add` | Add debt (structured or natural language) |
| `/debts` | List all debts with status |
| `/monthly` | Monthly payment summary |
| `/upcoming` | Upcoming 30 days payments |
| `/summary` | Quick financial snapshot |
| `/edit` | Edit an existing debt |
| `/delete` | Remove a debt entry |
| `/history` | Payment history |
| `/strategy` | Payoff strategy (snowball/avalanche) |
| `/login` | Get web dashboard login link |
| `/faq` | Frequently asked questions |

---

## 🧪 Demo

Try the web dashboard instantly:

- **URL:** [jatuhtempo.up.railway.app](https://jatuhtempo.up.railway.app)
- **Email:** `demo@jatuhtempo.app`
- **Password:** `demo123`

Or chat with the Telegram bot: [@jatuhtempo_bot](https://t.me/jatuhtempo_bot)

---

## 🏗 Architecture

```
jatuhtempo/
├── app/
│   ├── api/            # REST API endpoints
│   │   ├── auth.py     # Auth routes (login, register, demo)
│   │   ├── debts.py    # Debt CRUD
│   │   ├── payments.py # Payment tracking
│   │   ├── rates.py    # Interest rates
│   │   └── ocr.py      # OCR integration
│   ├── core/           # Config, auth, DB, security
│   │   ├── config.py   # App configuration
│   │   ├── database.py # DB engine + sessions
│   │   └── security.py # JWT, password hashing
│   ├── models/         # SQLAlchemy ORM models
│   ├── platforms/
│   │   └── telegram/   # Bot handlers, keyboards, FSM
│   │       ├── handlers/
│   │       └── keyboards/
│   ├── services/       # Business logic layer
│   └── schemas/        # Pydantic validation schemas
│
├── web/                # Next.js frontend
│   ├── src/
│   │   ├── app/        # App Router pages
│   │   └── components/ # Reusable UI components
│   └── public/         # Static assets
│
├── migrations/         # Alembic DB migrations
└── docker-compose.yml  # Container orchestration
```

---

## 🗺 Roadmap

```
Phase 1 ✅ (Current)
├── Core debt tracking (CRUD + installments)
├── AI OCR + natural language parsing ✓
├── Interest rate tracking + AI learning ✓
├── Payoff strategy engine ✓
├── Multi-platform (Telegram + Web) ✓
├── Smart reminder lifecycle ✓
├── Demo account ✓
└── Security hardening ✓

Phase 2 🚧 (Next)
├── Behavioral Nudge Engine
├── Personal Debt Health Score
├── Peluang — Opportunity Network (KOMBAT)
├── WhatsApp Bot
├── httpOnly cookies (production security)
├── i18n: English + multi-language
└── Subscription expiry enforcement

Phase 3 🔮 (Future)
├── AI Debt Autopilot
├── Debt Collapse Predictor
├── Screenshot Timeline Intelligence
├── Calendar Sync (Google, iCloud, Outlook)
├── Debt Negotiation Copilot
├── Debt Stress Score
└── Debt Buddy — Anonymous Community
```

---

## 📄 License

**PROPRIETARY SOFTWARE** — All Rights Reserved.

This repository and its contents are proprietary software owned by FMA Software Labs. Unauthorized copying, distribution, or use is strictly prohibited. See [LICENSE](LICENSE) for full terms.

© 2026 FMATheNomad. All rights reserved.

---

## 👨‍💻 About

Built by [**FMATheNomad**](https://github.com/FMATheNomad) as part of the **FMA Software Labs** ecosystem.

Supporting the **Komunitas Bebas Utang (KOMBAT)** by Guru Gembul — helping Indonesians achieve financial freedom through technology.

<p align="center">
  <sub>Made with ❤️ for Indonesia</sub>
</p>
