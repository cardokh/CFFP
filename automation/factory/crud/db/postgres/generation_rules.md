# PostgreSQL Database Automation Generation Rules

## Status

Frozen baseline for DB1.

These rules describe how database metadata may be generated for managed CFFP CRUD entities.

The AI provider must not rely on hidden assumptions or provider memory. All generated database metadata must follow this document, the task contract, the approved input metadata, and the existing repository conventions.

---

## Core Rule

The AI provider does not generate SQL directly.

The AI provider may only propose structured metadata that is later validated and processed by deterministic scripts.

```text
Approved entity input
        ↓
Proposed metadata
        ↓
Validation
        ↓
Schema metadata
        ↓
Seed metadata
        ↓
PostgreSQL schema generator
        ↓
PostgreSQL seed generator