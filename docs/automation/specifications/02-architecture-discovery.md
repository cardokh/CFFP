# CFFP Architecture Discovery

Version: Draft 2
Status: Living Document
Last Updated: June 2026

## Purpose

This document captures architectural discussions, decisions, assumptions, trade-offs, and future considerations related to the CFFP platform.

Unlike Architecture Decision Records (ADRs), which document finalized decisions, this document serves as a working architectural journal where ideas can be explored, challenged, refined, and revisited over time.

The purpose is to preserve architectural reasoning and avoid losing important discussions as the project evolves.

---

# Architectural Scope

This document focuses on architectural concerns.

Examples include:

* System architecture
* Module architecture
* Backend architecture
* Frontend architecture
* Security architecture
* Data architecture
* Integration architecture
* Deployment architecture
* Operational architecture

Platform vision, goals, business capabilities, and project motivation are documented separately in the Vision and Purpose document.

---

# Current Architectural Direction

The current architectural direction can be summarized as follows:

* Modular platform architecture
* Shared platform core
* Multi-organization support
* Modular monolith deployment
* Event-driven architecture readiness
* Microservice extraction readiness
* API-first backend architecture
* React-based frontend architecture
* Python-based backend architecture

These directions remain subject to refinement as the project evolves.

---

# Platform Architecture

## Platform Structure

The platform is expected to consist of:

* CCore
* Business Modules
* Shared Infrastructure
* Shared Services
* Shared User Experience Components

The platform should support the addition and removal of modules while minimizing impact on existing functionality.

---

# Core Platform (CCore)

CCore is the architectural foundation of the platform.

All business modules depend on CCore.

Current responsibilities include:

* Organizations
* Users
* Authentication
* Authorization
* Roles
* Permissions
* Module Management
* Menu Management
* User Preferences
* Themes
* Search
* Shared Navigation
* Shared Platform Services

CCore should remain independent from business-specific functionality.

Business functionality belongs in individual modules.

---

# Module Architecture

## Architectural Principles

Modules should be:

* Self-contained
* Cohesive
* Loosely coupled
* Independently testable
* Explicit in their dependencies

Modules should communicate through well-defined interfaces rather than through direct implementation dependencies whenever practical.

---

## Initial Modules

### CTime

Initial responsibilities include:

* Time registration
* Time reporting
* Approval workflows
* Organization ownership

### CLearn

Initial responsibilities include:

* Learning content
* Educational workflows
* Learning progress
* AI-assisted educational functionality

Additional modules may be introduced over time.

---

# Multi-Organization Architecture

The platform is expected to support multiple organizations.

Example:

Platform Owner
↓
Organization A
Organization B
Organization C

Each organization may contain:

* Users
* Roles
* Permissions
* Enabled Modules
* Menu Configuration

Organizations should be logically isolated.

Data belonging to one organization should not be accessible by another organization unless explicitly permitted by future architectural requirements.

The exact tenancy model remains open.

Possible approaches include:

* Shared database with organization identifiers
* Schema-per-organization
* Database-per-organization

Further discussion is required.

---

# Search Architecture

Search is considered a shared platform capability.

Search should be implemented centrally rather than independently within individual modules.

Long-term search targets may include:

* Menus
* Pages
* Modules
* User content
* Business entities
* Platform configuration

The search architecture remains open.

Possible future approaches include:

* Database-backed search
* Dedicated search indexing
* Search service abstraction

---

# Preferences and Themes Architecture

Preferences are considered a platform-level concern.

Examples include:

* Theme selection
* Layout preferences
* Accessibility preferences
* Future personalization settings

Preferences should be managed centrally through CCore.

The storage and configuration strategy remains open.

---

# Backend Architecture

## Primary Language

Current preferred decision:

Python

Reasoning:

* Strong AI ecosystem
* Strong automation ecosystem
* Strong scripting support
* Excellent tooling support
* Alignment with platform goals

Python is expected to be used for:

* Backend development
* Automation
* Tooling
* Testing
* AI integration
* Development scripts

---

## Backend Framework

Current status:

Not finalized.

Primary candidates:

* FastAPI
* Django

Current direction:

FastAPI is currently preferred.

Reasons include:

* Greater architectural freedom
* API-first design
* Lightweight architecture
* Strong ecosystem alignment

Django remains a viable alternative because of its built-in support for:

* Authentication
* Authorization
* Administration
* ORM
* CRUD infrastructure

Final decision remains open.

---

## Dependency Injection

Current direction:

Use dependency injection throughout the backend architecture.

Goals:

* Reduced coupling
* Improved testability
* Explicit dependencies
* Future service extraction readiness

Implementation approach remains open.

---

## Service Layer

Current direction:

Business logic should be implemented within dedicated service classes.

Goals:

* Separation of concerns
* Reusability
* Testability
* Maintainability

Controllers and API endpoints should remain thin.

---

## Repository Layer

Current direction:

Data access should be isolated behind repository abstractions.

Goals:

* Persistence isolation
* Testability
* Flexibility for future changes

Repository design remains open.

---

## API Design

Current direction:

API-first architecture.

Goals:

* Clear module boundaries
* Frontend independence
* Future integration support
* Future service extraction support

API standards remain open.

---

# Frontend Architecture

## Frontend Framework

Current preferred decision:

React + TypeScript

Reasons:

* Strong ecosystem
* Industry adoption
* Flexible architecture
* Excellent tooling
* Strong testing support

Angular was evaluated but is not currently preferred.

---

## Frontend Structure

Current direction:

Feature-oriented organization.

Potential structure:

* Shared Components
* Shared Services
* Platform Shell
* Module Features

Structure remains subject to refinement.

---

## Platform Shell

The platform should provide a shared shell that contains:

* Navigation
* Menus
* Search
* User settings
* Theme support

Modules should integrate into the shell rather than implementing their own platform-level navigation.

---

# Modular Monolith

## Current Architectural Strategy

Current preferred deployment model:

Modular Monolith

Characteristics:

* Single deployable application
* Shared database
* Shared authentication
* Shared infrastructure

Modules remain logically separated despite sharing a deployment unit.

---

## Architectural Principles

The platform should maintain:

* Strong module boundaries
* Explicit dependencies
* Clear ownership
* Independent testing

The goal is to maintain modularity regardless of deployment topology.

---

# Microservice Readiness

The platform does not currently plan to implement microservices.

However, the architecture should allow future extraction.

Current strategy:

* Self-contained modules
* Explicit dependencies
* Service abstractions
* Dependency injection
* Minimal coupling

Guiding principle:

Design for extraction, do not optimize for extraction.

---

# Event-Driven Architecture

## Current Strategy

The platform should support internal domain events.

Examples:

* UserCreated
* OrganizationCreated
* ModuleEnabled
* TimesheetSubmitted
* LessonCompleted

Events should be published and consumed internally within the application.

---

## Future Evolution

The project does not currently plan to introduce:

* Kafka
* RabbitMQ
* Distributed messaging infrastructure

However, event contracts should be designed so that future migration remains possible.

Guiding principle:

Design event boundaries now, keep infrastructure simple.

---

# Development Environment

## Source Control

Current decision:

GitHub

Purpose:

* Source control
* Collaboration
* CI/CD integration

---

## Project Management

Current decision:

Jira

Purpose:

* Backlog management
* Planning
* Tracking
* Architectural work management

---

## CI/CD

Current decision:

GitHub Actions

Purpose:

* Build automation
* Test automation
* Deployment automation

---

## IDE

Current preferred decision:

Visual Studio Code

Visual Studio remains a possible secondary tool.

---

# Agentic Development

The project intends to actively explore AI-assisted development environments.

Potential tools include:

* GitHub Copilot
* Cursor
* Windsurf
* Claude Code
* Future agentic development environments

This area remains under active exploration.

---

# Open Architectural Topics

The following areas require future discussion:

* Database selection
* ORM strategy
* Authentication strategy
* Authorization strategy
* Deployment architecture
* Docker strategy
* Cloud strategy
* Test automation architecture
* API standards
* Logging strategy
* Monitoring strategy
* Observability strategy
* Design system architecture
* Accessibility architecture
* Documentation standards
* ADR process

---

# Candidate ADRs

The following topics are likely candidates for future Architecture Decision Records:

* Python as primary language
* FastAPI vs Django
* React + TypeScript
* Modular Monolith architecture
* Multi-organization strategy
* Authentication strategy
* Authorization strategy
* Database strategy
* Event-driven architecture approach
* Docker strategy
* Deployment strategy

---

# Guiding Principle

Build the simplest architecture that supports today's requirements while preserving the ability to evolve into more advanced architectures tomorrow.

Examples:

* Modular Monolith today → Microservices later
* Internal Events today → Distributed Events later
* Shared Deployment today → Distributed Deployment later

Evolution should be enabled by architecture rather than forced by premature complexity.
