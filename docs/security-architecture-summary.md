# Security Architecture Summary

Version: 1.0
Status: Completed
Last Updated: June 2026

## Purpose

This document summarizes the decisions made during the Security Architecture epic.

The goal is to capture the agreed architectural direction for authentication, authorization, roles, permissions, organization isolation, and session management.

This document serves as a high-level reference and checkpoint before implementation begins.

---

# Security Architecture Scope

The Security Architecture epic covered:

* Authentication
* Authorization
* Role Model
* Permission Model
* Organization Isolation
* Session and Token Strategy

Completed stories:

* ARCH-7 Authentication Strategy
* ARCH-8 Authorization Strategy
* ARCH-9 Role Model
* ARCH-10 Permission Model
* ARCH-11 Organization Isolation
* ARCH-12 Session / Token Strategy

---

# Final Architecture Overview

The agreed security flow is:

User
→ Authentication
→ Session
→ Organization Context
→ Role Assignment
→ Permission Evaluation
→ Authorized Action

Authentication determines who the user is.

Authorization determines what the user is allowed to do.

Permissions are evaluated within the active organization context.

---

# ARCH-7 Authentication Strategy

## Decision

Authentication is a CCore responsibility.

Authentication is implemented behind an abstraction layer so that authentication providers can be replaced without affecting consumers.

Examples:

* Internal username/password
* Azure AD
* Google
* SAML
* OpenID Connect

## Architectural Principle

Consumers depend on authentication contracts rather than authentication implementations.

This follows the same architectural principle used for repositories and persistence abstraction.

## Status

Decision completed.

---

# ARCH-8 Authorization Strategy

## Decision

Authorization is centralized within CCore.

Modules do not implement independent authorization systems.

Authorization decisions are based on permissions assigned through roles.

## Architectural Principle

Single source of truth for authorization.

## Status

Decision completed.

---

# ARCH-9 Role Model

## Decision

Users are assigned roles.

Roles are assigned permissions.

Users are not assigned permissions directly.

Initial roles are platform-managed.

Examples:

* Platform Administrator
* Organization Administrator
* Manager
* User

Custom organization-defined roles may be introduced in future versions.

## Status

Decision completed.

---

# ARCH-10 Permission Model

## Decision

Permissions represent actual authority.

Roles act as containers for permissions.

Permissions are owned either by:

* CCore
* Individual Modules

Examples:

CCore:

* organization.manage
* module.enable
* user.manage

CTime:

* time.submit
* time.approve

CLearn:

* learn.lesson.start
* learn.lesson.edit

## Architectural Principle

Permission ownership follows module ownership.

## Status

Decision completed.

---

# ARCH-11 Organization Isolation

## Decision

The platform supports multiple organizations.

Users may belong to multiple organizations.

Authentication identifies the user.

Organization context determines:

* Roles
* Permissions
* Data access
* Module access

The active organization becomes part of every authorization decision.

## Architectural Principle

Organization context is explicit.

## Status

Decision completed.

---

# ARCH-12 Session / Token Strategy

## Decision

The initial implementation uses server-side sessions.

Authentication establishes identity.

Sessions represent authenticated state.

The session implementation is hidden behind an abstraction.

Future implementations may use:

* JWT
* OAuth
* OpenID Connect
* External Identity Providers

without affecting consumers.

## Architectural Principle

Session implementation must be replaceable.

## Status

Decision completed.

---

# Architectural Decisions Requiring ADRs

The following decisions should eventually become formal ADRs:

* Authentication Strategy
* Authorization Strategy
* Role Model
* Permission Model
* Organization Isolation
* Session Strategy

ADR creation is not required before implementation begins.

---

# Future Security Topics

The following topics remain open and may require future architecture stories.

## User Lifecycle

Topics:

* User creation
* User invitation
* User deactivation
* User deletion

Priority:

Medium

---

## Password Management

Topics:

* Password policy
* Password reset
* Password complexity
* Password storage

Priority:

Medium

---

## Audit Logging

Topics:

* Login auditing
* Permission changes
* Role changes
* Administrative actions

Priority:

High

---

## Organization Membership Management

Topics:

* Add user to organization
* Remove user from organization
* Organization ownership

Priority:

Medium

---

## Secrets Management

Topics:

* Environment variables
* Secret storage
* External secret providers

Priority:

Low for CCore v1

---

# Implementation Backlog Created by Security Architecture

The Security Architecture epic creates the need for the following implementation work.

## CCore Domain Objects

* User
* Organization
* Role
* Permission
* Session

---

## CCore Services

* Authentication Service
* Authorization Service
* Session Service
* Organization Context Service
* Role Service
* Permission Service

---

## CCore Persistence

* User Repository
* Organization Repository
* Role Repository
* Permission Repository
* Session Repository

---

## CCore APIs

* Login
* Logout
* Session Validation
* Organization Selection
* User Management
* Role Management
* Permission Management

---

# Security Architecture Completion Assessment

The Security Architecture epic is considered complete.

The architecture is internally consistent.

No blocking architectural gaps have been identified.

The remaining open topics are implementation details or future enhancements rather than blockers.

---

# Recommended Next Step

Proceed to the Core Platform Architecture epic.

Primary focus:

* CCore module structure
* Backend layering
* Dependency Injection strategy
* API architecture
* Repository architecture
* Domain event architecture

The goal is to establish where the security architecture components will live inside the platform and prepare for the first working CCore implementation.
