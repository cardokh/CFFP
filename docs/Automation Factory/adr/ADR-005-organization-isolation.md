# ADR-005 Organization Isolation

Status: Accepted

Date: 2026-06-08

## Context

CFFP is designed as a multi-organization platform.

The platform must support multiple organizations operating within the same deployment while maintaining logical separation of users, permissions, data, configuration, and business functionality.

Examples include:

* Platform Owner Organization
* Customer Organizations
* Demonstration Organizations
* Future Partner Organizations

A single user may belong to multiple organizations and may perform different responsibilities within each organization.

The architecture therefore requires a clear organizational boundary model that prevents unauthorized access across organizations while allowing future platform growth.

## Decision

CFFP will implement organization-based isolation.

Organizations represent logical security and ownership boundaries within the platform.

Users may belong to one or more organizations.

Authentication identifies the user.

Organization selection establishes the active organizational context.

Authorization decisions are evaluated within the active organization context.

Roles, permissions, module access, and business data are organization-specific.

Every request requiring authorization must operate within an explicitly defined organization context.

## Organization Model

Example:

```text id="8ljyvg"
Platform Owner
        │
 ┌──────┼──────┐
 │      │      │
Org A  Org B  Org C
```

Each organization may contain:

* Users
* Roles
* Permissions
* Enabled Modules
* Configuration
* Business Data

Organizations are logically isolated from one another.

## User Membership Model

A user may belong to multiple organizations.

Example:

```text id="9s7i0g"
cardo@example.com

    ├─ Organization A
    │      └─ Manager
    │
    ├─ Organization B
    │      └─ User
    │
    └─ Organization C
           └─ Organization Administrator
```

The same authenticated user may have different responsibilities depending on the active organization.

## Authorization Context

Authorization must always consider:

```text id="v8x4ne"
User
    +
Active Organization
    +
Permissions
```

Permission evaluation without an organization context is not permitted.

Organization context forms part of every authorization decision.

## Data Isolation

Data ownership belongs to organizations.

Business data created within one organization must not be accessible by another organization unless explicitly supported by future architectural requirements.

Examples:

* Users
* Timesheets
* Learning Content
* Reports
* Configuration

All business data must be associated with an organization.

The physical storage strategy remains an implementation concern and is outside the scope of this ADR.

## Alternatives Considered

### Single Organization Platform

Assume only one organization exists.

#### Rejected

This would significantly limit platform flexibility and contradict the long-term platform vision.

Multi-organization support is a core architectural requirement.

---

### Separate Deployments per Organization

Deploy an independent platform instance for each organization.

#### Rejected

This increases operational complexity and reduces the value of a shared platform architecture.

The preferred approach is a shared platform with logical organization isolation.

---

### User-Centric Security Model

Security decisions based solely on users and roles.

#### Rejected

This does not adequately support multi-organization membership and creates ambiguity when users belong to multiple organizations.

Organization context is required.

## Consequences

### Positive

* Supports multi-tenant architecture.
* Supports multiple customers.
* Supports multiple business domains.
* Supports future SaaS evolution.
* Clear ownership boundaries.
* Consistent security model.
* Supports users belonging to multiple organizations.
* Aligns with enterprise platform architecture.

### Negative

* Additional complexity in authorization.
* Additional complexity in data access.
* Organization context must be maintained throughout request processing.
* Requires careful implementation to avoid data leakage.

## Future Evolution

Future enhancements may include:

* Organization hierarchies
* Parent-child organizations
* Shared services between organizations
* Cross-organization collaboration
* Organization templates
* Organization provisioning automation
* Advanced tenancy models

Potential future storage approaches may include:

* Shared database with organization identifiers
* Schema-per-organization
* Database-per-organization

These decisions remain outside the scope of this ADR and may be addressed separately.

## Relationship to Other Decisions

Organization isolation affects:

* Authentication
* Authorization
* Roles
* Permissions
* Data Ownership
* Module Access

The security model becomes:

```text id="xnq1zb"
User
    ↓
Authentication
    ↓
Session
    ↓
Organization Context
    ↓
Role Assignment
    ↓
Permission Evaluation
    ↓
Authorized Action
```

Organization context is therefore a fundamental part of the platform security architecture.

## Related Decisions

* ADR-001 Authentication Strategy
* ADR-002 Authorization Strategy
* ADR-003 Role Model
* ADR-004 Permission Model
* ADR-006 Session Strategy
