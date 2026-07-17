# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.



## What this is

A dashboard that ingests a user's job-application emails (via Gmail), classifies them with an LLM
(company + application status), and displays them as a Kanban board. See `plan.md` for the full
design discussion and rationale — read it before implementing any of the areas marked as stubs below.

Stack: FastAPI backend (`backend/`), React/Vite frontend (`frontend/`), Postgres for storage, Claude
(Anthropic API) for email classification.

## Commands

Postgres (local dev):
```
docker compose up -d
```

Backend (from `backend/`):
```
cp .env.example .env        # then fill in ANTHROPIC_API_KEY, DATABASE_URL, etc.
uv sync
uv run uvicorn app.main:app --reload
```

Frontend (from `frontend/`):
```
npm install
npm run dev
```

No test suite, linter, or formatter is configured yet in either project.

## Architecture

**This is boilerplate, not a finished app.** Several core pieces are intentionally stubbed with
`raise NotImplementedError` rather than implemented:

- `backend/app/llm/client.py::classify_email` — no prompt or output schema yet.
- `backend/app/auth/google.py` (`/auth/google/login`, `/auth/google/callback`) — no OAuth flow yet.
- `backend/app/sync/gmail_sync.py::sync_user_mailbox` — no Gmail History API sync logic yet.
- `backend/app/db.py` defines only the SQLAlchemy `engine`/`SessionLocal`/`Base` plumbing — no models.
  The database schema (applications table, status state machine, multi-tenant `user_id` columns, etc.)
  has not been designed.

Don't "fix" these by filling them in casually — the classification prompt/schema, OAuth flow, sync
logic, and DB schema are all substantial design decisions covered in `plan.md`. Implement them
deliberately, not as a side effect of an unrelated task.

**Backend request flow**: `app/main.py` creates the FastAPI app and mounts `app/api/router.py`, which
aggregates the applications router and the Google auth router. `app/config.py` loads settings from
environment variables via `pydantic-settings` (see `.env.example` for the full list) — note that
`Settings()` is instantiated at import time, so importing `app.config` (directly or via `app.db` /
`app.llm.client`) without a valid `.env` will fail immediately.

**`GET/PATCH /api/applications`** currently serves hardcoded in-memory mock data
(`app/api/applications.py`) instead of querying Postgres — this exists solely so the Kanban board has
something to render before the real schema/sync pipeline exists. Replace it once models exist.

**Frontend**: `KanbanBoard.jsx` groups cards by whatever `status` string each application object has —
column names are not hardcoded anywhere in the frontend. This means the UI already supports whatever
status state machine gets designed on the backend, with no frontend changes required. Drag-and-drop
uses native HTML5 DnD (no external library); dropping a card PATCHes `/api/applications/{id}` with the
new status. In dev, Vite proxies `/api` to `http://localhost:8000` (see `vite.config.js`); the FastAPI
app also has CORS enabled for `http://localhost:5173` as a fallback.
