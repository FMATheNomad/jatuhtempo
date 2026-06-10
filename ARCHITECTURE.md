# JatuhTempo — Complete Architecture Document

**Generated:** June 11, 2026
**Project Root:** `/home/fariz/Destop/all-project-running/fma-micro-saas-ecosystems/jatuhtempo`
**Tech Stack:** Python 3.14 + FastAPI + SQLAlchemy (async) + PostgreSQL + Aiogram 3 + Next.js 14 + TailwindCSS
**Deployment:** Railway (Docker — single container serving both API and static files)

---

## 1. HIGH-LEVEL ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                      JatuhTempo System                              │
├────────────────────┬────────────────────┬───────────────────────────┤
│   Telegram Bot     │   Web Frontend     │   REST API (FastAPI)      │
│   (Aiogram 3)      │   (Next.js 14)     │   /api/*                   │
│                    │                    │                           │
│  ┌──────────────┐  │  ┌──────────────┐  │  ┌───────────────────┐   │
│  │ Commands     │  │  │ Pages        │  │  │ Auth API          │   │
│  │ Messages     │  │  │ Components   │  │  │ Debts API         │   │
│  │ Callbacks    │  │  │ API Client   │  │  │ Polar API         │   │
│  │ AddDebt FSM  │  │  │              │  │  │ OCR Endpoint      │   │
│  └──────┬───────┘  │  └──────┬───────┘  │  └────────┬──────────┘   │
│         │          │         │           │           │              │
└─────────┼──────────┴─────────┼───────────┴───────────┼──────────────┘
          │                    │                       │
          └────────────────────┼───────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Service Layer      │
                    │   (Business Logic)   │
                    │                      │
                    │  debt_service        │
                    │  ai_parser           │
                    │  ocr_service         │
                    │  platform_matcher    │
                    │  payment_service     │
                    │  polar_service       │
                    │  audit_service       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Database           │
                    │   (PostgreSQL)       │
                    │   via SQLAlchemy     │
                    │   async + asyncpg    │
                    └─────────────────────┘
```

**Background Processes:**
- APScheduler: Runs `check_reminders` every 1 min + `check_wa_unlinked` every 4-8 hours
- Telegram Bot Polling: Long-running asyncio task polling updates from Telegram

---

## 2. DATABASE MODEL — ALL TABLES & RELATIONSHIPS

### 2.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐       ┌──────────────────────┐
│      users      │       │       debts          │       │     reminders        │
├─────────────────┤       ├─────────────────────┤       ├──────────────────────┤
│ id (UUID, PK)   │──┐    │ id (UUID, PK)        │──┐    │ id (UUID, PK)        │
│ telegram_id     │  │    │ user_id (UUID, FK)    │──│───▶│ debt_id (UUID, FK)   │
│ email           │  │    │ platform (String)     │  │    │ user_id (UUID, FK)   │
│ password_hash   │  │    │ amount (Integer)      │  │    │ remind_at (DateTime) │
│ nama            │  │    │ due_date (Date)       │  │    │ type (String)        │
│ phone_number    │  │    │ installment_current   │  │    │ sent (Boolean)       │
│ wa_linked_at    │  │    │ installment_total     │  │    └──────────────────────┘
│ wa_reminder_    │  │    │ category (String)     │  │
│   optout        │  │    │ notes (String)        │  │
│ polar_customer_ │  │    │ status (Enum)         │  │
│   id            │  │    │   → active            │  │
│ subscription_   │  │    │   → paid              │  │
│   status        │  │    │   → late              │  │
│ created_at      │  │    │ source (Enum)         │  │
└─────────────────┘  │    │   → screenshot         │  │
                     │    │   → manual             │  │
                     │    │ paid_at (DateTime)     │  │
                     │    │ created_at             │  │
                     │    │ updated_at             │  │
                     │    └────────────────────────┘  │
                     │                                │
                     │    ┌─────────────────────┐     │
                     │    │     payments         │     │
                     │    ├─────────────────────┤     │
                     └───▶│ id (UUID, PK)        │     │
                          │ debt_id (UUID, FK)───┘     │
                          │ user_id (UUID, FK)─────────┘
                          │ amount_paid (Int)
                          │ paid_at (DateTime)
                          │ notes (String?)
                          └─────────────────────┘

┌──────────────────────┐      ┌──────────────────────────┐
│    audit_logs         │      │  platform_signatures     │
├──────────────────────┤      ├──────────────────────────┤
│ id (UUID, PK)         │      │ id (UUID, PK)            │
│ user_id (UUID, FK)───▶users  │ platform (String, idx)   │
│ action (String)       │      │ keyword (String)         │
│ resource (String)     │      │ weight (Integer)         │
│ resource_id (String?) │      │ source (String)          │
│ detail (Text?)        │      │   → manual, ai,          │
│ ip_address (String?)  │      │     correction           │
│ created_at            │      │ created_at               │
└──────────────────────┘      └──────────────────────────┘

┌──────────────────────┐
│    ocr_logs           │
├──────────────────────┤
│ id (UUID, PK)         │
│ user_id (UUID, FK)───▶users
│ image_path (String?)  │
│ raw_text (Text,       │
│   encrypted via       │
│   Fernet)             │
│ parsed_json (JSON)    │
│ created_at            │
└──────────────────────┘
```

### 2.2 Column Details

**users** — 11 columns
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| telegram_id | BigInteger | Unique, Indexed, Nullable |
| email | String(255) | Unique, Indexed, Nullable |
| password_hash | String(255) | Nullable |
| nama | String(255) | Nullable |
| phone_number | String(20) | Nullable |
| wa_linked_at | DateTime(tz) | Nullable |
| wa_reminder_optout | Boolean | Default false |
| polar_customer_id | String(100) | Nullable |
| subscription_status | String(20) | Default "free" |
| created_at | DateTime(tz) | Default now() |

**debts** — 13 columns
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id, NOT NULL |
| platform | String(100) | NOT NULL |
| amount | Integer | NOT NULL (Rupiah) |
| due_date | Date | NOT NULL |
| installment_current | Integer | Nullable |
| installment_total | Integer | Nullable |
| category | String(100) | Nullable |
| notes | String(500) | Nullable |
| status | Enum(active,paid,late) | Default active |
| source | Enum(screenshot,manual) | Default manual |
| paid_at | DateTime(tz) | Nullable |
| created_at/updated_at | DateTime(tz) | Auto |

**payments** — 5 columns
**reminders** — 5 columns
**audit_logs** — 6 columns
**ocr_logs** — 5 columns (+ JSON column for parsed data)
**platform_signatures** — 5 columns

---

## 3. API ENDPOINTS — COMPLETE REFERENCE

### 3.1 Auth Routes (`/api/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register with email+password. Returns session_token. |
| POST | `/api/auth/login-web` | None | Login with email+password. Returns session_token. |
| POST | `/api/auth/login` | None | Login with Telegram login_token (JWT). Returns session_token. |
| POST | `/api/auth/link-telegram` | Bearer + body token | Links Telegram account to existing web account. |
| GET | `/api/auth/verify` | None | Verifies a session token. Returns valid+user info. |

### 3.2 Debt Routes (`/api`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/debts` | Bearer | List debts. Query: `?status=active&platform=Kredivo` |
| GET | `/api/debts/summary` | Bearer | Monthly summary (active count, total, paid this month, upcoming) |
| GET | `/api/debts/upcoming` | Bearer | Upcoming debts in N days (default 30). Query: `?days=30` |
| POST | `/api/debts` | Bearer | Create debt. Body: `{platform, amount, due_date, ...}` |
| PATCH | `/api/debts/{id}` | Bearer | Update debt fields. |
| DELETE | `/api/debts/{id}` | Bearer | Delete debt (owner-only). |
| GET | `/api/debts/{id}/payments` | Bearer | Get payment history for a debt. |
| PATCH | `/api/debts/{id}/status` | Bearer | Update status (active/paid/late). Auto-creates Payment if paid. |

### 3.3 User Routes (`/api`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/user/me` | Bearer | Get current user profile. |
| PUT | `/api/user/phone` | Bearer | Update WhatsApp phone number. |

### 3.4 OCR & Platform Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/ocr` | Bearer | Upload image → OCR → AI parse → return structured data. |
| POST | `/api/platform/learn` | Bearer | Submit correction for platform matching. |

### 3.5 Polar.sh Routes (Subscription/Payment)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/polar/checkout` | Bearer | Create Polar checkout URL for Pro subscription. |
| POST | `/api/polar/webhook` | None (signed) | Handle `order.paid` and `subscription.active` events. |

### 3.6 Public Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check (used by Railway) |
| GET | `/api/stats` | None | Public stats (total user count) |
| GET | `/` | None | Static file serving (Next.js build output) |

### 3.7 Auth Flow

**JWT Tokens (2 types):**
- **login_token:** exp=5min, type="login", payload={telegram_id}
- **session_token:** exp=7days, type="session", payload={telegram_id?, user_id}

**Web Login Flow:**
1. Telegram user types `/login` → Bot generates 5-min login_token → sends link `web_url/login?token=...`
2. User clicks link → Browser POSTs token to `/api/auth/login` → gets session_token → stored in localStorage

**Email Login Flow (Web-only):**
1. User fills email+password form → POST to `/api/auth/login-web` → bcrypt verify → returns session_token

**Telegram Linking Flow:**
1. User already logged in on web, wants to link Telegram
2. Bot generates login_token, user brings it to web
3. Web calls `/api/auth/link-telegram` with session Bearer + login_token in body

---

## 4. TELEGRAM BOT — ALL COMMANDS & FLOWS

### 4.1 Command Handlers (`commands.py`)

| Command | Description | Key Behavior |
|---------|-------------|-------------|
| `/start` | Welcome + stats or onboarding | Checks if user has debts; shows stats or welcome |
| `/help` | Command reference | Lists all commands with examples |
| `/add` | Add debt (inline or FSM) | Parses inline args OR launches FSM wizard (see add_debt.py) |
| `/debts` | List debts | Supports `--status active/paid/late` and `--platform` filters |
| `/monthly` | Monthly recap | Calls get_monthly_summary, shows active/paid/upcoming |
| `/upcoming` | Debts due in 30 days | Calls get_upcoming_debts |
| `/summary` | Quick summary | Shows active count, paid this month, upcoming count |
| `/delete` | Delete debt | Accepts full UUID or 8-char prefix match |
| `/edit` | Edit debt fields | Supports `--amount`, `--due_date`, `--platform`, `--status`, `--cicilan`, `--kategori`, `--notes` |
| `/history` | Payment history for a debt | Shows all Payment records with remaining balance |
| `/login` | Generate web login link | Creates 5-min JWT login_token, sends URL |
| `/wa` | Set WhatsApp number | Stores formatted +62 number or removes it |
| `/strategy` | Snowball payoff strategy | Sorts active debts by amount ascending, gives payoff order |

### 4.2 Message Handler (`messages.py`)

| Trigger | Description |
|---------|-------------|
| `F.photo` | Receives photo message → downloads → Tesseract OCR → DeepSeek AI parse → shows preview with confirm/cancel keyboard |

### 4.3 Callback Handlers (`callbacks.py`)

| Callback Data | Description |
|---------------|-------------|
| `paid:{debt_id}` | Mark debt as paid (with celebration message) |
| `late:{debt_id}` | Mark debt as late |
| `ocr_confirm` | Accept OCR parsed data → save as Debt with source=screenshot |
| `ocr_cancel` | Cancel OCR result, clean up temp files |
| `wa_optout` | Opt out of WhatsApp reminder nagging |

### 4.4 AddDebt FSM (`add_debt.py`)

A 5-step wizard with Aiogram FSM:

```
Platform Select → Amount Input → Due Date Input → Installment Select → Category Select → Confirm
(Inline KB)      (Text)          (Text)            (Inline KB)        (Inline KB)     (Inline KB)
```

States: `AddDebt` with fields: platform, amount, due_date, installment, category, confirm

### 4.5 Inline Keyboards (`keyboards/inline.py`)

- `debt_keyboard(debt_id)`: [✅ Lunas] [🔴 Terlambat]
- `confirm_keyboard()`: [✅ Simpan] [❌ Batal]

---

## 5. FRONTEND — ALL PAGES & COMPONENTS

### 5.1 Page Map

| Route | File | Type | Auth Required | API Dependencies |
|-------|------|------|---------------|-----------------|
| `/` | page.tsx | Landing (unauthed) / Dashboard (authed) | Conditional | getSummary, getDebts |
| `/login` | login/page.tsx | Login/Register | No | POST /api/auth/login, /api/auth/login-web, /api/auth/register |
| `/debts` | debts/page.tsx | Debt list + CRUD | Yes | GET/POST/PATCH/DELETE /api/debts, POST /api/ocr, PATCH /api/debts/{id}/status |
| `/history` | history/page.tsx | Payment history | Yes | GET /api/debts, GET /api/debts/{id}/payments |
| `/monthly` | monthly/page.tsx | Monthly summary | Yes | GET /api/debts/summary |
| `/upcoming` | upcoming/page.tsx | Upcoming debts | Yes | GET /api/debts/upcoming |
| `/settings` | settings/page.tsx | Profile, Telegram link, WA, Subscription | Yes | GET /api/user/me, PUT /api/user/phone, GET /api/polar/checkout |
| `/strategy` | strategy/page.tsx | Snowball strategy + simulator | Yes | GET /api/debts |
| `/docs` | docs/page.tsx | Documentation index | No | None (static) |
| `/faq` | faq/page.tsx | FAQ page | No | None (static) |
| `/legal/terms` | legal/terms/page.tsx | Terms & Conditions | No | None (static) |
| `/legal/privacy` | legal/privacy/page.tsx | Privacy Policy | No | None (static) |
| `/docs/*` | Static markdown files | Getting Started, OCR Guide, Telegram Bot | No | None (static) |
| `/health` | health/route.ts | API health check | No | None |

### 5.2 Component Tree

```
RootLayout (html lang="id")
├── LandingPage (unauthed)
│   ├── Hero Section (gradient-hero)
│   ├── Features Section (4 cards)
│   └── Footer
├── DashboardPage (authed) - page.tsx
│   ├── Sidebar
│   │   ├── Logo
│   │   ├── Nav links: Dashboard, Utang, Bulanan, Akan Datang, Strategi, Riwayat, Pengaturan
│   │   └── Logout button
│   ├── Header
│   │   ├── Page Title
│   │   └── MobileNav (hamburger drawer)
│   ├── SummaryCards (4 cards: active count, total amount, paid this month, upcoming count)
│   ├── Quick Add Form
│   └── Recent Debts (top 5)
├── DebtsPage (/debts)
│   ├── OCR Upload (drag&drop + file input)
│   ├── Add/Edit Form (platform select, amount, due_date, etc.)
│   ├── Search + Status Filter
│   └── Debt List (mobile: cards, desktop: table)
│       ├── Active Debts section
│       └── Paid Debts section
├── MonthlyPage (/monthly)
│   ├── 4 Stat Cards (active, total, paid count, paid amount)
│   └── Upcoming Bills table
├── UpcomingPage (/upcoming)
│   ├── 3 Stat Cards (count, total, average)
│   └── Sorted debt table
├── StrategyPage (/strategy)
│   ├── 3 Stat Cards (total, monthly, count)
│   ├── Snowball order list
│   └── Simulator (slider + income-based)
├── SettingsPage (/settings)
│   ├── Profile Card
│   ├── Link Telegram Card (when not linked)
│   ├── Subscription Card (upgrade to Pro)
│   ├── WhatsApp Card (input phone)
│   └── Logout
├── LoginPage (/login)
│   ├── Token Login (from Telegram)
│   └── Email Login/Register
├── DocsPage (/docs)
├── FAQPage (/faq)
├── TermsPage (/legal/terms)
└── PrivacyPage (/legal/privacy)
```

### 5.3 Shared Components

| Component | Path | Props |
|-----------|------|-------|
| Sidebar | `components/layout/sidebar.tsx` | None (reads pathname) |
| MobileNav | `components/layout/mobile-nav.tsx` | None (reads pathname) |
| SummaryCards | `components/dashboard/summary-cards.tsx` | `{summary: MonthlySummary}` |
| Badge | `components/ui/badge.tsx` | `{variant: 'default'|'active'|'paid'|'late'|'outline'}` |
| Button | `components/ui/button.tsx` | `{variant, size, ...}` |
| Card | `components/ui/card.tsx` | Children + CardHeader, CardTitle, CardDescription, CardContent |

### 5.4 API Client (`lib/api.ts`)

Centralized fetch wrapper with Bearer token injection, 401 auto-redirect, and typed responses. Exports:
- `getDebts()`, `getSummary()`, `getUpcoming()`, `getPayments()`
- `createDebt()`, `updateDebt()`, `deleteDebtApi()`, `updateDebtStatus()`
- `getUser()`, `updatePhone()`
- `getCheckoutUrl()`, `loginWithToken()`

---

## 6. SERVICE LAYER — DETAILED FUNCTIONALITY

### 6.1 debt_service.py
Core business logic for debt CRUD, reminders, user management.
- `get_or_create_user()` — Find by telegram_id or create new User
- `create_debt()` — Create Debt + auto-create 5 Reminder records (H-7, H-3, H-1, due, overdue)
- `get_user_debts()` — List with optional status/platform filters
- `get_monthly_summary()` — Aggregation query (active count, sum, paid this month, upcoming)
- `get_upcoming_debts()` — Debts due within N days
- `update_debt()` — Generic update with auto-payment creation when marked paid
- `update_debt_status()` — Status change + auto Payment record creation
- `delete_debt()` — Cascade deletes reminders
- `update_user_wa()` — Set/remove phone number and optout

### 6.2 ai_parser.py
DeepSeek API integration for structured data extraction from OCR text.
- Indonesian-language system prompt for debt extraction
- Handles Indonesian number format (Rp1.000.000 → 1000000)
- `parse_debt_from_text()` → POST to DeepSeek chat completions → parse JSON → clean + validate
- Returns: platform, amount, due_date, installment_current/total, category, notes

### 6.3 ocr_service.py
Local Tesseract OCR via pytesseract.
- `ocr_image()` → opens image → runs `tesseract image_to_string` with `lang=ind+eng` → returns text

### 6.4 platform_matcher.py
Keyword-based scoring system for platform identification.
- **Seed data:** 50+ keyword→platform mappings in `SEED_SIGNATURES` (Akulaku, Kredivo, Shopee PayLater, GoPay Later, Home Credit, FIF, Adira, Kredit Pintar, EasyCash, BCA, Mandiri)
- `seed_signatures()` — One-time DB seed on app startup
- `match_platform()` — Score-based matching with tiebreaker (needs >3 point lead)
- `learn_from_correction()` — Extracts significant words from corrected text, adds new signatures with +/- weights

### 6.5 payment_service.py
- `create_payment()` — Insert Payment record
- `get_payments_for_debt()` — List payments for a debt, newest first

### 6.6 polar_service.py
Polar.sh integration for subscription management.
- `create_checkout_url()` — Creates Polar checkout with `telegram_id` in metadata

### 6.7 audit_service.py
- `log_audit()` — Insert AuditLog entry (user_id, action, resource, resource_id, detail, ip)

---

## 7. BACKGROUND PROCESSES

### 7.1 Scheduler (`scheduler.py`)
Initialized in `app/main.py` lifespan via `start_scheduler()`.

**Job 1: check_reminders** (every `reminder_check_interval_minutes` = default 1 min)
1. Query all Reminders where `remind_at <= now AND sent = false`
2. For each: build message with label + debt details
3. Send via Telegram bot with debt_keyboard inline buttons
4. Mark `sent = true`

**Job 2: check_wa_unlinked** (every 4-8 hours, randomized)
1. Query Users where phone_number IS NULL AND wa_reminder_optout = false
2. Send reminder to link WhatsApp
3. Re-schedule with random interval

### 7.2 Bot Polling
Started as asyncio task in app lifespan. Runs `dp.start_polling(bot, skip_updates=True)`.
Handles commands, messages, and callbacks concurrently.

---

## 8. DATA FLOW — KEY OPERATIONS

### 8.1 Add Debt (Telegram /add)
```
User → /add Kredivo 350000 2026-07-15
  → commands.cmd_add()
    → parse inline args (shlex)
    → get_or_create_user(session, telegram_id)
    → create_debt(session, user_id, DebtCreate(...), source=manual)
      → INSERT Debt
      → INSERT 5 Reminders (H-7, H-3, H-1, due, overdue)
    → reply with debt keyboard
```

### 8.2 Add Debt (Web Form)
```
User fills form → clicks Tambah
  → debts page → POST /api/debts
    → api/debts.create_debt_endpoint()
      → Depends(get_current_user) → verify JWT → find User
      → create_debt(session, user_id, DebtCreate(...))
        → same as above
      → log_audit("create", "debt")
    → return DebtResponse
```

### 8.3 OCR Flow (Telegram Photo)
```
User sends screenshot → messages.handle_photo()
  → download image to media/
  → ocr_image() → Tesseract OCR → raw_text
  → parse_debt_from_text(raw_text) → DeepSeek API → structured data
  → match_platform(raw_text, session) → keyword scoring
  → store_ocr(user_id, {parsed, raw_text, image_path}) → temp store (5min TTL)
  → show preview with confirm_keyboard()
  → User taps ✅ Simpan → callbacks.callback_ocr_confirm()
    → pop_ocr(user_id) → retrieve from temp
    → create_debt(session, user_id, ..., source=screenshot)
    → OcrLog created (image_path, encrypted raw_text, parsed_json)
    → cleanup: delete image file
```

### 8.4 OCR Flow (Web Upload)
```
User drops image on web → /debts page
  → fetch POST /api/ocr (FormData with image)
    → ocr_upload() → save to media/ → ocr_image() → parse_debt_from_text()
    → match_platform() → return {raw_text, parsed}
  → User sees preview → clicks Simpan
    → fetch POST /api/debts with parsed data
```

### 8.5 Login Flow (Telegram → Web)
```
User types /login in Telegram
  → commands.cmd_login()
    → create_login_token(telegram_id) → JWT (5 min)
    → send message with URL: {web_url}/login?token={jwt}
  → User clicks link
    → login page reads ?token= from URL
    → POST /api/auth/login {token}
      → verify JWT → find user by telegram_id
      → create_session_token() → return session_token (7 days)
    → store in localStorage → redirect to / dashboard
```

### 8.6 Payment/Status Update
```
User marks debt as paid (via Telegram button)
  → callbacks.callback_paid()
    → update_debt_status(session, debt_id, DebtStatus.paid)
      → set debt.status = "paid"
      → set debt.paid_at = now
      → INSERT Payment(debt_id, user_id, amount_paid=debt.amount)
    → celebration message with random emoji + encouragement

Same via Web:
  → fetch PATCH /api/debts/{id}/status {status: "paid"}
    → patch_debt_status()
      → update_debt_status()
      → log_audit("update_status", "debt")
```

### 8.7 Subscription Checkout Flow
```
User clicks Upgrade to Pro (Web settings or Telegram)
  → GET /api/polar/checkout (auth required)
    → polar_service.create_checkout_url(telegram_id)
      → Polar SDK create checkout with metadata: {telegram_id}
      → return checkout URL
  → User completes payment on Polar.sh
  → Polar sends webhook POST /api/polar/webhook
    → Verify signature (POLAR_WEBHOOK_SECRET)
    → event "order.paid" or "subscription.active"
    → Extract telegram_id from metadata
    → Find User by telegram_id
    → Set subscription_status = "pro"
    → Set polar_customer_id
```

---

## 9. SECURITY & INFRASTRUCTURE

### 9.1 Middleware Stack (applied in order)
1. **CORSMiddleware** — Allows web_url origin (or all if not set)
2. **SecurityHeadersMiddleware** — X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-XSS-Protection, Cache-Control for static assets
3. **RateLimitMiddleware** — 30 requests per 60 seconds per IP on /api/* routes

### 9.2 Auth Security
- JWT tokens with HS256, configured via JWT_SECRET env var
- Session tokens: 7-day expiry, login tokens: 5-min expiry
- bcrypt password hashing via passlib[bcrypt]
- Telegram bot rate limiting: 1 command per second per user (in-memory dict)

### 9.3 Data Encryption
- OCR raw_text stored encrypted via Fernet (PBKDF2-derived key from ENCRYPTION_KEY)
- Encryption key derived via SHA-256 PBKDF2 with salt "jatuh-tempo-salt", 100K iterations

### 9.4 Deployment
- **Docker:** Single multi-stage container
  - Stage 1: Node 20-alpine builds Next.js → static output
  - Stage 2: Python 3.14-slim with Tesseract OCR + indo language pack
  - Copies Next.js output to `/app/web-out`
  - Serves API + static files from same uvicorn process
- **Railway:** Dockerfile build, health check on `/health`, 300s timeout
- **Database:** PostgreSQL via SQLAlchemy async engine + asyncpg driver

---

## 10. PLATFORM DEFINITIONS

Defined in `app/core/platforms.py` (backend) and `web/src/lib/platforms.ts` (frontend):

**Platforms (22):**
Akulaku, Kredivo, Shopee PayLater, GoPay Later, Dana, SPayLater, Home Credit, FIF, Adira, Kredit Pintar, EasyCash, Danamon, Mandiri, BCA, BNI, BRI, CIMB Niaga, Maybank, Permata, Pinjaman Teman, Pinjaman Keluarga, Cash / Tunai, Lainnya

**Categories (7):**
pinjol, paylater, kredit, bank, teman, cash, lainnya

---

## 11. FILE DEPENDENCY GRAPH

```
app/main.py
  ├── app.core.config (settings)
  ├── app.core.db (init_db)
  ├── app.core.scheduler (start_scheduler, set_bot_instance)
  ├── app.core.ratelimit_mw (RateLimitMiddleware)
  ├── app.core.security_mw (SecurityHeadersMiddleware)
  ├── app.api.auth (auth_router)
  ├── app.api.debts (debts_router)
  ├── app.api.polar (polar_router)
  └── app.platforms.telegram.bot (get_bot)

app.api.auth.py
  ├── app.core.auth (verify_token, create_*_token)
  ├── app.core.db (async_session_factory)
  └── app.models.user

app.api.debts.py
  ├── app.core.auth (verify_token)
  ├── app.core.db (async_session_factory)
  ├── app.models.debt
  ├── app.schemas.debt
  ├── app.services.debt_service
  ├── app.services.payment_service
  ├── app.services.ocr_service
  ├── app.services.ai_parser
  ├── app.services.audit_service
  └── app.services.platform_matcher

app.services.debt_service.py
  ├── app.models.debt, payment, reminder, user
  └── app.schemas.debt

app.services.ai_parser.py
  ├── app.core.config (settings)
  └── httpx (DeepSeek API call)

app.services.platform_matcher.py
  ├── app.core.platforms (PLATFORMS)
  └── app.models.platform_signature

app.platforms.telegram.bot.py
  ├── app.core.config
  └── app.platforms.telegram.handlers.*

app.platforms.telegram.handlers.commands.py
  ├── app.core.db, auth, ratelimit
  ├── app.schemas.debt
  ├── app.services.* (debt_service, payment_service)
  └── app.platforms.telegram.keyboards.inline

app.platforms.telegram.handlers.messages.py
  ├── app.core.db, config, ratelimit, temp_store
  ├── app.models.ocr_log
  ├── app.services.* (ai_parser, debt_service, ocr_service)
  └── app.platforms.telegram.keyboards.inline

app.platforms.telegram.handlers.callbacks.py
  ├── app.core.db, crypto, temp_store
  ├── app.models.ocr_log, debt
  ├── app.schemas.debt
  ├── app.services.* (debt_service)
  └── app.platforms.telegram.keyboards.inline

app.platforms.telegram.handlers.add_debt.py
  ├── app.core.db, config, platforms, ratelimit
  ├── app.schemas.debt
  ├── app.services.* (debt_service)
  └── app.platforms.telegram.keyboards.inline

web/src/lib/api.ts (used by every authenticated page)
web/src/lib/platforms.ts (used by debts page)
web/src/components/layout/sidebar.tsx (used by all dashboard pages)
web/src/components/layout/mobile-nav.tsx (used by all dashboard pages)
web/src/components/dashboard/summary-cards.tsx (used by home page)
```

---

## 12. CONFIGURATION (ENVIRONMENT VARIABLES)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| DATABASE_URL | postgresql+asyncpg://... | ✅ | PostgreSQL connection string |
| JWT_SECRET | "" | ✅ | JWT signing secret |
| ENCRYPTION_KEY | "" | ✅ | Fernet encryption key base |
| TELEGRAM_BOT_TOKEN | "" | Optional | Telegram bot token (disables bot if empty) |
| DEEPSEEK_API_KEY | "" | ✅ | DeepSeek API key |
| DEEPSEEK_BASE_URL | https://api.deepseek.com | No | DeepSeek API base URL |
| DEEPSEEK_MODEL | deepseek-v4-flash | No | DeepSeek model name |
| WEB_URL | "" | ✅ | Web app URL (CORS + login links) |
| POLAR_ACCESS_TOKEN | "" | Optional | Polar.sh API token |
| POLAR_PRODUCT_ID | "" | Optional | Polar product ID for Pro subscription |
| POLAR_SUCCESS_URL | "" | Optional | Post-checkout redirect URL |
| POLAR_WEBHOOK_SECRET | "" | Optional | Polar webhook signing secret |
| REMINDER_CHECK_INTERVAL_MINUTES | 1 | No | How often to check reminders |
| MAX_IMAGE_SIZE_MB | 10 | No | Max upload size for OCR images |
| DEBUG | false | No | SQLAlchemy echo mode |

---

## 13. KEY DESIGN PATTERNS & OBSERVATIONS

1. **Hybrid Auth Model:** Users can register via email (bcrypt) or auto-create via Telegram (telegram_id). Both paths converge to the same User table. Session tokens are JWT-based, stored in localStorage on web.

2. **Dual-Interface Consistency:** The same business logic (`debt_service.py`) serves both the Telegram bot and the Web API. The bot has additional features like inline keyboards and FSM wizards that the web doesn't need, but the core operations are shared.

3. **OCR Pipeline:** Image → Tesseract (local, lang=ind+eng) → raw_text → DeepSeek LLM (structured extraction) → platform_matcher (keyword scoring) → structured debt data. The platform_matcher is a fallback/correction layer that improves over time via user corrections.

4. **Automatic Reminder System:** When any debt is created, 5 reminder records are automatically generated (H-7, H-3, H-1, due, overdue). The scheduler checks every minute and sends via Telegram when due. This is a clean pull-based approach (no cron daemon needed).

5. **Subscription via Polar.sh:** Pro features are planned though not heavily gated in the current code. The Polar integration creates checkout URLs and handles webhooks for order.paid/subscription.active events.

6. **In-Memory Temp Store for OCR:** OCR results are stored in a Python dict with 5-minute TTL (`temp_store.py`). This avoids writing incomplete OCR data to the database before user confirmation.

7. **Platform Matching as Learning System:** The PlatformSignature table acts as a trainable classifier. Seed data is loaded on first startup, and user corrections add weighted keywords, allowing the system to improve platform detection over time without model retraining.

8. **No Microservices:** This is a monolithic application. Both the API server and the Telegram bot run in the same Python process, sharing the same event loop and database session factory. The Next.js frontend is built to static files and served by FastAPI as a static mount.
