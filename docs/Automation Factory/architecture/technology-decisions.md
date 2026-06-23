# Automation Factory Technology Decisions

## Purpose

This document records the technology facts that the CRUD generation pipeline must use as source-of-truth. The generator must not infer or guess these values.

## Inspected Baseline

The current repository baseline shows the following CCore implementation facts:

| Area | Current baseline |
|---|---|
| Backend language | Python |
| HTTP framework/style | Custom route registry/dispatcher over Python handlers |
| CCore golden reference | `backend/src/ccore/tasks` |
| Frontend golden reference | `frontend/static/desktop/protected/ccore/tasks.html`, `task-details.html`, `css/tasks.css`, `css/task-details.css`, `js/tasks.js`, `js/task-details.js` |
| Database manager | `backend/src/ccore/infrastructure/database.py` |
| CCore database connection | PostgreSQL through `psycopg2` |
| Database config | `scripts/db/postgres/config/database.json` |
| Schema scripts | `scripts/db/postgres/postgres_create_schema.py` and config JSON |
| Seed scripts | `scripts/db/postgres/postgres_seed_data.py` and config JSON |
| Backend domain objects | `dataclasses` |
| API request contracts | Explicit parser classes, not Pydantic in current CCore baseline |
| Async database sessions | Not present in current CCore baseline |
| Frontend | Static HTML, vanilla JavaScript, existing shared CSS |
| Styling | Existing shared CSS files, not Tailwind in current CCore baseline |
| AI provider infrastructure | Factory contains Gemini-related provider/tests/configuration |
| Orchestration infrastructure | Factory contains Prefect provider/flow/test infrastructure |

## No-Guessing Rule

The generation pipeline must never silently switch technology choices.

If the user wants a different target from the current baseline, such as Pydantic v2, async database sessions, SQLAlchemy, Tailwind, or another database layer, that must be documented as an explicit migration decision before generation.

## Current Decision for First CRUD Generation Experiment

For the first Organization CRUD generation experiment, the generator should follow the current repository baseline unless the user explicitly changes this document.

Therefore:

- Use PostgreSQL artifacts/configuration because the current CCore baseline uses PostgreSQL.
- Use synchronous `psycopg2` repository style because that is what the current CCore repository uses.
- Use dataclass domain objects and explicit request parser contracts because `ccore_tasks` uses that pattern.
- Use vanilla JavaScript and existing shared CSS because the current CCore frontend uses that pattern.
- Use the CCore Task CRUD implementation as the golden reference.

## Explicit Non-Decisions

These are not selected for the first generation experiment unless the user changes the architecture deliberately:

- Pydantic v2 schemas.
- Async database sessions.
- Tailwind styling.
- SQLAlchemy ORM.
- Direct AI edits to repository files without staging and validation.
