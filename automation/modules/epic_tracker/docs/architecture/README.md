# Architecture Documentation

## Purpose

This folder contains architecture-level documentation for the Epic Tracker module.

## Current Scope

The current iteration only defines structure and documentation. It does not introduce runtime orchestration, code generation, schemas, or validation logic.

## Key Decisions

- `automation/modules/epic_tracker/` is a reusable automation module.
- `automation/factory/` remains the implementation area for existing and future factory pipelines.
- Application-specific work belongs under `applications/`.
- Documentation-only contracts currently live under `docs/contracts/`.
- Module-level validation and reports define shared conventions for the Epic Tracker as a whole.
