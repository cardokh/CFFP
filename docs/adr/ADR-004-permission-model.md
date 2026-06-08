# ADR-004 Permission Model

Status: Accepted

Date: 2026-06-08

## Context

CFFP requires a consistent mechanism for representing authority throughout the platform.

While roles provide a convenient way to group users, roles alone are not sufficiently flexible for long-term platform evolution.

The platform is expected to support:

* Multiple organizations
* Multiple business modules
* Platform capabilities
* Future module expansion
* Future customization

A permission-based model allows authorization decisions to remain independent of specific role names and provides a more flexible foundation for future growth.

The platform therefore requires a clearly defined permission architecture.

## Decision

Permissions represent actual authority within the platform.

Authorization decisions will be based on permissions.

Roles act as containers for permissions.

Users receive permissions indirectly through role assignments.

Permissions are owned by either:

* CCore
* Individual business modules

Each module is responsible for defining and maintaining its own permissions.

CCore is responsible for platform-level permissions.

Permission evaluation will be performed through the centralized Authorization Service.

Permissions must be evaluated within the active organization context.

## Permission Ownership

### CCore Permissions

Examples:

```text
user.view
user.create
user.update
user.delete

organization.view
organization.manage

role.view
role.manage

permission.view
permission.manage

module.enable
module.disable
```

These permissions represent platform-level capabilities.

---

### Module Permissions

Examples:

CTime:

```text
time.view
time.create
time.submit
time.approve
time.report
```

CLearn:

```text
learn.lesson.start
learn.lesson.complete
learn.lesson.edit
learn.lesson.publish
```

Modules own their permissions and remain responsible for defining them.

## Permission Naming Strategy

Permissions should follow a consistent naming convention.

Recommended format:

```text
resource.action
```

Examples:

```text
user.view
user.create

organization.manage

time.submit
time.approve

learn.lesson.start
```

For more complex domains:

```text
module.resource.action
```

Examples:

```text
learn.lesson.publish
learn.course.manage
```

Permission names should remain stable and descriptive.

## Alternatives Considered

### Role-Based Authorization Only

Use role names directly for authorization decisions.

Example:

```text
Administrator
Manager
User
```

#### Rejected

Roles represent groups of permissions rather than authority itself.

Using roles directly creates rigid authorization models and makes future evolution difficult.

---

### Direct User Permissions

Assign permissions directly to users.

#### Rejected

This creates administrative complexity and does not scale effectively.

Role-based assignment provides a cleaner and more manageable approach.

---

### Module-Specific Permission Models

Allow each module to implement its own permission architecture.

#### Rejected

This would create inconsistent authorization behavior and undermine the centralized security model.

Modules may define permissions but authorization remains centralized.

## Consequences

### Positive

* Flexible authorization model.
* Consistent security architecture.
* Clear ownership boundaries.
* Supports modular platform growth.
* Easier auditing.
* Easier testing.
* Reduced coupling to role names.
* Enterprise-friendly approach.

### Negative

* Permission catalog must be maintained.
* Permission naming standards must be enforced.
* Additional administration required as the platform grows.

## Future Evolution

Future enhancements may include:

* Permission groups
* Permission templates
* Permission hierarchies
* Dynamic permissions
* Context-aware permissions
* Delegated permission administration
* Organization-defined permissions

These capabilities should be introduced only when justified by actual platform needs.

The initial implementation should remain simple and focused on a clear permission catalog.

## Relationship to Other Decisions

Permissions are the fundamental unit of authority.

The authorization flow is:

```text
User
    ↓
Role Assignment
    ↓
Permissions
    ↓
Authorization Decision
```

Authorization evaluates permissions rather than role names.

Permissions are assigned through roles and evaluated within the active organization context.

## Related Decisions

* ADR-002 Authorization Strategy
* ADR-003 Role Model
* ADR-005 Organization Isolation
* ADR-006 Session Strategy
