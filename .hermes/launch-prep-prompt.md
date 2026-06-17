# JatuhTempo — Full SaaS Launch Preparation Prompt

You are a senior full-stack developer. Fix ALL items below in order. Project at `/home/fariz/Destop/all-project-running/fma-micro-saas-ecosystems/jatuhtempo`. Python 3.14, FastAPI, Next.js 14, PostgreSQL, Docker, Railway.

## CRITICAL (Blockers — Fix First)

### 1. Fix `is_admin()` — Pro users must NOT be admins
**File:** `app/core/admin.py`
**Problem:** Line 7-8: `if user.subscription_status == "pro": return True` makes EVERY paying user an admin.
**Fix:** Remove the `subscription_status == "pro"` check entirely. Admin is determined ONLY by `ADMIN_EMAILS` env var. Run existing tests after change.

### 2. Add missing Polar.sh webhook event handlers
**File:** `app/api/polar.py`
**Problem:** Only handles `order.paid` and `subscription.active`. Missing `subscription.canceled`, `subscription.revoked`, `order.refunded`.
**Fix:** Add handlers for these three events. Each should:
- Find user by `telegram_id` from metadata or `polar_customer_id`
- Set `subscription_status = "free"`
- Clear `polar_customer_id = None`
- Log the change
- Keep the existing event handlers working

Also fix the ImportError silent skip (line 43-44): remove the try/except around webhook verification. If polar_sdk is missing, the app should fail at import time, not silently skip.

### 3. Fix free tier limit inconsistency
**File:** `app/api/debts.py` line 343-345
**Problem:** Code checks `active_count >= 10` but error message says "Batas 5 utang aktif gratis".
**Fix:** Change the check to `active_count >= 5` (or pick 10 and update the message — be consistent). Update the error message to match. Also update the FAQ at `web/src/app/faq/page.tsx` line 22 to match: change "10 utang aktif" to whatever number you chose.

### 4. Remove fake hardcoded stats from landing page
**File:** `web/src/app/page.tsx` lines 138-155
**Problem:** Stats section shows hardcoded "Rp1.2M+", "1K+", "95%" — these are fake.
**Fix:** Replace the Stats section with data from `/api/stats` endpoint. Fetch on mount and display real numbers. If data is not available yet, either hide the section entirely or show a graceful fallback ("Data akan muncul setelah kamu mulai menggunakan JatuhTempo").

## HIGH (Fix Before Launch)

### 5. Fix webhook verification — remove silent import skip
**File:** `app/api/polar.py`
**Fix:** Remove try/except around `validate_event`. If `polar_sdk.webhooks` can't be imported, let it crash. Or move the import to the top of the file so it fails on app startup, not silently at runtime.

### 6. Add email rate limiting on forgot-password
**File:** `app/api/auth.py`
**Problem:** `/forgot-password` has IP rate limit but no per-email rate limit.
**Fix:** Add a dict `_password_reset_rates: dict[str, list[float]]` keyed by email. Allow max 1 request per 300 seconds per email. Same sliding window pattern as `_auth_rates`.

### 7. Add token revocation / server-side logout
**File:** `app/api/auth.py` (new endpoint) + `app/core/auth.py` (new function)
**Problem:** No way to invalidate JWT sessions. localStorage removal is client-only.
**Fix:**
- Create a simple token blacklist: `_blacklisted_tokens: set[str]` (in-memory is OK for MVP, document that it resets on restart)
- Add `POST /api/auth/logout` endpoint: takes `Authorization: Bearer <token>`, adds token hash to blacklist
- Modify `verify_token()` to check blacklist before returning payload
- Update the logout button in `web/src/app/settings/page.tsx` to call `/api/auth/logout` before clearing localStorage

## MEDIUM (Should Fix Soon)

### 8. Expose delete account in Settings UI
**File:** `web/src/app/settings/page.tsx`
**Problem:** Backend has `POST /api/auth/delete-account` but Settings page doesn't have the button.
**Fix:** Add a "Hapus Akun" section at the bottom of Settings page:
- Red/destructive styled button
- Confirmation modal: "Apakah kamu yakin? Semua data utang, pembayaran, dan pengingat akan dihapus permanen."
- On confirm: `fetch('/api/auth/delete-account', { method: 'POST', headers: { Authorization: 'Bearer ' + token } })`
- On success: clear localStorage, redirect to landing page
- Show error message if fails

### 9. Fix mobile touch targets (WCAG compliance)
Search all `h-9` and bare `h-10` classes on interactive elements across all page.tsx files in `web/src/app/`. Replace with `min-h-[44px]` pattern where needed.
Specifically check:
- `web/src/app/upcoming/page.tsx` — select filter uses `h-9`
- Any button/input that's interactive should have minimum 44px touch target

### 10. Add proper Indonesian meta title
**File:** `web/src/app/layout.tsx` line 9
**Change:** `title: 'JatuhTempo — Kelola Utang dengan AI'` (instead of English "Debt Management")

## VERIFICATION

After all fixes:
1. Run backend tests: `cd /home/fariz/.../jatuhtempo && python -m pytest tests/ -v`
2. Start the app: `uvicorn app.main:app --reload` on a separate terminal, then:
   - `curl http://localhost:8000/health` returns 200
   - `curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test123","nama":"Test"}'` returns session_token
3. Build frontend: `cd web && npm run build` passes without errors
4. Verify no fake stats remain in landing page source

## RULES
- Read each file fully before editing
- Use search_files to find all occurrences before making changes
- Run tests after each critical fix
- Do NOT modify database schema, models, or migrations
- Do NOT modify deployment config (Dockerfile, railway.json, CI)
- Always use patch() for targeted edits, avoid rewriting entire files
- Report what you changed and what tests pass
