# CFFP Architecture Discovery

Version: Draft 1
Status: Living Document
Last Updated: June 2026

## Purpose

This document captures architectural discussions, decisions, assumptions, trade-offs, and future considerations related to the CFFP platform.

Unlike Architecture Decision Records (ADRs), which document finalized decisions, this document serves as a working architectural journal where ideas can be explored, challenged, refined, and revisited over time.

The purpose is to preserve architectural reasoning and avoid losing important discussions as the project evolves.

---

# Current Architectural Direction

The current architectural direction is based on the principles defined in the Vision and Purpose document.

At a high level, CFFP is expected to become:

* A modular software platform.
* Multi-organization capable.
* User and permission driven.
* AI-assisted in both development and future platform capabilities.
* Designed according to HCI principles.
* Built with automation and testability as primary concerns.
* Designed for long-term maintainability.

---

# Platform Architecture

## Platform Rather Than Application

A major architectural decision is that CFFP is being designed as a platform rather than a standalone application.

The platform consists of:

* Shared core services.
* Shared infrastructure.
* Shared user experience components.
* Pluggable business modules.

The platform itself is considered the primary product.

Individual modules serve as demonstrations of platform capabilities.

---

# Core Platform (CCore)

CCore is the architectural foundation of the platform.

All modules depend upon CCore.

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

Business functionality belongs in modules.

---

# Initial Platform Modules

## CTime

Purpose:

* Demonstrate platform modularity.
* Demonstrate CRUD workflows.
* Demonstrate organization ownership.
* Demonstrate permissions and authorization.

The timesheet module is intentionally simple but realistic.

---

## CLearn (Working Name)

Purpose:

* Evolve concepts from the LLA project.
* Demonstrate educational functionality.
* Demonstrate AI-related possibilities.
* Demonstrate that different business domains can coexist within the same platform.

---

# Multi-Organization Model

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

Organizations should be isolated from one another.

Users should only access data belonging to organizations for which they have permissions.

---

# User Experience Principles

The project places strong emphasis on Human-Computer Interaction (HCI).

The platform should be:

* Discoverable
* Configurable
* Efficient
* Consistent
* Accessible

Architecture should support these goals rather than treating them as purely visual concerns.

---

# Global Search

One capability identified early is global platform search.

Long-term goals include searching:

* Menus
* Pages
* Modules
* User content
* Business entities
* Platform configuration

Search should be implemented as a shared platform capability rather than as independent module features.

---

# Preferences and Themes

Preferences are considered a core platform responsibility.

Examples include:

* Light mode
* Dark mode
* Theme selection
* Layout preferences
* Future accessibility settings

Preferences should be stored per user and managed through CCore.

---

# Backend Architecture

## Primary Language

Current Preferred Decision:

Python

Reasoning:

* Strong AI ecosystem
* Strong automation ecosystem
* Strong scripting support
* Existing team familiarity
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

Current Status:

Not finalized.

Primary candidates:

* FastAPI
* Django

Current Direction:

FastAPI is currently the preferred option.

Reasoning:

* Greater architectural freedom.
* Better alignment with API-first design.
* Strong AI ecosystem alignment.
* Better support for designing platform architecture from first principles.
* Encourages explicit architecture rather than framework-driven architecture.

Django remains a strong alternative because of its built-in support for:

* Authentication
* Authorization
* Administration
* ORM
* CRUD infrastructure

Final decision remains open.

---

# Frontend Architecture

## Frontend Framework

Current Preferred Decision:

React + TypeScript

Reasoning:

* Industry adoption.
* Strong ecosystem.
* Flexible architecture.
* Good alignment with FastAPI.
* Excellent testing support.
* Good AI tooling support.

Angular was evaluated but is not currently preferred.

Reasoning:

* More opinionated.
* Heavier framework.
* Less architectural flexibility.

This decision may be revisited if future requirements change.

---

# Modular Monolith

## Current Architectural Strategy

Current preferred deployment architecture:

Modular Monolith

Meaning:

* Single deployable application.
* Shared database.
* Shared authentication.
* Shared infrastructure.

Modules remain logically separated despite sharing a deployment unit.

---

## Reasoning

Advantages:

* Simpler deployment.
* Easier debugging.
* Easier testing.
* Lower operational complexity.
* Faster development.

The platform should remain architecturally modular even while physically deployed as a single application.

---

# Microservice Readiness

The project does not currently plan to implement microservices.

However, the architecture should be designed to allow future extraction.

Current strategy:

* Self-contained modules.
* Clear ownership boundaries.
* Explicit dependencies.
* Dependency injection.
* Minimal coupling.

This means individual modules may eventually be extracted into independent services if a future need arises.

The project follows:

"Design for extraction, do not optimize for extraction."

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

These events should be published within the application and handled through an internal event mechanism.

---

## Future Evolution

The project does not currently plan to introduce:

* Kafka
* RabbitMQ
* Distributed messaging infrastructure

However, events should be designed in a way that allows future migration if desired.

Current principle:

"Design event boundaries now, keep infrastructure simple."

This preserves the ability to demonstrate event-driven architecture later without introducing unnecessary complexity today.

---

# AI-Assisted Software Engineering

AI is considered a core development practice.

AI may assist with:

* Architecture discussions
* Design reviews
* Documentation
* Code generation
* Refactoring
* Testing
* Automation

Architecture ownership remains human-led.

AI acts as an assistant rather than an architect.

---

# Automation Strategy

Automation is considered a primary architectural concern.

The goal is to automate repetitive engineering tasks wherever practical.

Examples:

* Testing
* Validation
* Documentation
* Database setup
* Environment setup
* Quality checks
* Build processes

Automation should be introduced continuously throughout development.

---

# Python Tooling Philosophy

Python scripts are considered first-class engineering assets.

Scripts should be:

* Reusable
* Configurable
* Logged
* Structured
* Maintainable

The approach should build upon lessons learned from the LLA project.

---

# Development Environment

## Source Control

Current Decision:

GitHub

Purpose:

* Source control
* Collaboration
* CI/CD integration

---

## Project Management

Current Decision:

Jira

Purpose:

* Backlog management
* Epics
* Stories
* Tasks
* Architectural planning

---

## CI/CD

Current Decision:

GitHub Actions

Purpose:

* Build automation
* Test automation
* Deployment automation

---

## IDE

Current Preferred Decision:

Visual Studio Code

Reasoning:

* Strong Python support.
* Strong React support.
* Strong GitHub integration.
* Strong AI tooling support.
* Lightweight and flexible.

Visual Studio remains a possible secondary tool but is not currently preferred.

---

# Agentic Development

The project intends to actively explore AI-assisted development environments.

Potential tools include:

* GitHub Copilot
* Cursor
* Windsurf
* Claude Code
* Future agentic development environments

This topic remains under active exploration.

---

# Open Topics

The following areas require future discussion:

* Database selection
* ORM strategy
* Authentication strategy
* Authorization strategy
* Deployment architecture
* Docker strategy
* Cloud strategy
* Test automation framework selection
* API standards
* Logging strategy
* Monitoring and observability
* Design system
* Accessibility strategy
* Documentation standards
* Architecture Decision Record process

These topics will be explored in future architecture sessions.

---

# Guiding Principle

The platform should be designed according to the following principle:

Build the simplest architecture that supports today's requirements while preserving the ability to evolve into more advanced architectures tomorrow.

Examples:

* Modular Monolith today → Microservices later.
* Internal Events today → Kafka later.
* Shared Deployment today → Distributed Deployment later.

Evolution should be enabled by architecture rather than forced by premature complexity.
