# JatuhTempo

AI-powered debt management assistant. Track, remind, and eliminate debt via Telegram and Web.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Backend | Python 3.14, FastAPI, SQLAlchemy (async), PostgreSQL |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Bot | Aiogram 3 (Telegram) |
| AI | DeepSeek API |
| Deploy | Docker, Railway |

## Getting Started

```bash
git clone https://github.com/FMATheNomad/jatuhtempo.git
cd jatuhtempo

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your keys
uvicorn app.main:app --reload

# Frontend
cd web
npm install
npm run dev
```

## Environment

See `.env.example` for required variables.

## Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## License

Proprietary — FMA Software Labs
