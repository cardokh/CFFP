# ADR-002 Authorization Strategy

Status: Accepted

Date: 2026-06-08

## Context

CFFP requires a consistent and centralized mechanism for determining what authenticated users are allowed to do within the platform.

The platform is expected to support multiple organizations, multiple modules, different user roles, and future platform growth.

Without a centralized authorization model, modules could implement authorization independently, resulting in inconsistent behavior, duplicated logic, increased maintenance effort, and potential security vulnerabilities.

Authorization decisions must remain consistent across all platform capabilities and business modules.

## Decision

Authorization will be owned by CCore.

All authorization decisions will be performed through a centralized Authorization Service.

Business modules must not implement independent authorization mechanisms.

Authorization decisions will be based on permissions assigned through roles.

Authorization evaluation will occur within the active organization context.

The authorization architecture will be independent from authentication.

Authentication determines who the user is.

Authorization determines what the user is allowed to do.

Consumers requiring authorization decisions must depend on the Authorization Service contract rather than implementing permission evaluation directly.

## Alternatives Considered

### Module-Specific Authorization

Each module implements its own authorization model.

#### Rejected

This would create inconsistent security behavior across the platform and introduce duplicated authorization logic.

It would also make auditing, maintenance, testing, and future enhancements significantly more difficult.

---

### Role-Based Authorization Only

Use roles directly for authorization decisions.

Example:

* Administrator
* Manager
* User

#### Rejected

Roles represent groups of permissions rather than authority itself.

Direct role evaluation creates rigid systems that become difficult to evolve over time.

Permissions provide a more flexible and scalable authorization model.

---

### Hardcoded Authorization Rules

Implement authorization rules directly inside business logic.

#### Rejected

This creates tight coupling between business functionality and security concerns.

It reduces maintainability and makes future changes significantly more difficult.

## Consequences

### Positive

* Single source of truth for authorization.
* Consistent security behavior.
* Improved maintainability.
* Easier auditing.
* Easier testing.
* Simplified module development.
* Supports future platform growth.
* Supports future permission expansion.

### Negative

* Additional infrastructure required inside CCore.
* Authorization becomes a core platform responsibility.
* Modules depend on shared authorization services.

## Future Evolution

Future enhancements may include:

* Permission caching
* Dynamic permission evaluation
* Policy-based authorization
* Attribute-based authorization
* Organization-specific custom roles
* Organization-specific custom permissions
* Administrative permission management interfaces

The authorization model should evolve without requiring modules to implement authorization independently.

## Relationship to Other Decisions

Authentication and authorization are intentionally separated.

Authentication establishes identity.

Authorization evaluates authority.

Authorization depends on:

* ADR-001 Authentication Strategy
* ADR-003 Role Model
* ADR-004 Permission Model
* ADR-005 Organization Isolation

## Related Decisions

* ADR-001 Authentication Strategy
* ADR-003 Role Model
* ADR-004 Permission Model
* ADR-005 Organization Isolation
