# ADR-003 Role Model

Status: Accepted

Date: 2026-06-08

## Context

CFFP requires a scalable mechanism for grouping permissions and assigning authority to users.

The platform is expected to support:

* Multiple organizations
* Multiple business modules
* Different categories of users
* Future platform growth
* Future customization capabilities

Managing permissions directly on individual users would become increasingly difficult as the platform evolves.

A role-based approach provides a structured mechanism for assigning authority while maintaining flexibility and maintainability.

## Decision

CFFP will use a Role-Based Access Control (RBAC) model.

Users are assigned one or more roles.

Roles are assigned permissions.

Permissions represent actual authority.

Users are not assigned permissions directly.

Authorization decisions are based on permissions rather than role names.

Roles act as containers for permissions.

The initial implementation will use platform-managed roles defined by CCore.

Example roles include:

* Platform Administrator
* Organization Administrator
* Manager
* User

Roles may differ between organizations.

A user may have different roles in different organizations.

Role assignments are evaluated within the active organization context.

## Alternatives Considered

### Direct User Permissions

Assign permissions directly to users.

#### Rejected

This becomes difficult to manage as the number of users and permissions increases.

Permission administration becomes error-prone and difficult to audit.

The approach does not scale well for enterprise environments.

---

### Role Evaluation Without Permissions

Use role names directly during authorization.

Example:

```text
if role == Administrator
```

#### Rejected

This creates rigid authorization rules and tightly couples business functionality to specific role names.

Future changes become difficult and require code modifications.

Permissions provide a more flexible and maintainable model.

---

### Fully Custom Roles from Day One

Allow organizations to create unlimited custom roles immediately.

#### Rejected

This introduces additional complexity before the platform has proven its core architecture.

The initial platform should start with a small set of platform-managed roles.

Custom roles can be introduced later if required.

## Consequences

### Positive

* Simplified administration.
* Scalable permission management.
* Improved maintainability.
* Consistent authorization model.
* Easier auditing.
* Supports multiple organizations.
* Supports future platform growth.
* Aligns with common enterprise security practices.

### Negative

* Additional role management infrastructure required.
* Role definitions must be maintained.
* Poorly designed roles can lead to permission sprawl if not governed carefully.

## Future Evolution

Future enhancements may include:

* Organization-defined custom roles
* Role templates
* Role cloning
* Role inheritance
* Delegated role administration
* Dynamic role assignment
* Temporary role assignments

These capabilities should be introduced only when justified by platform requirements.

The initial implementation should remain simple and focused on platform-managed roles.

## Relationship to Other Decisions

Roles are not evaluated directly during authorization.

Permissions remain the fundamental unit of authority.

The relationship is:

```text
User
    ↓
Role
    ↓
Permission
```

Authorization evaluates permissions.

Roles serve as a management and grouping mechanism.

## Related Decisions

* ADR-001 Authentication Strategy
* ADR-002 Authorization Strategy
* ADR-004 Permission Model
* ADR-005 Organization Isolation
