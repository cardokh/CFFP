# ADR-006 Session Strategy

Status: Accepted

Date: 2026-06-08

## Context

After a user has successfully authenticated, the platform requires a mechanism for maintaining authenticated state across multiple requests.

Authentication establishes user identity, but authentication alone does not provide an efficient way to track authenticated users throughout a session.

The platform must support:

* Secure authenticated sessions
* Session timeout
* Session termination
* User logout
* Future authentication evolution
* Future identity provider integration

The platform should initially favor simplicity, security, maintainability, and architectural clarity over premature complexity.

## Decision

CFFP will initially use a server-side session model.

Authentication establishes user identity.

Session management maintains authenticated state.

Session management is considered a separate concern from authentication.

A dedicated Session Service will be responsible for:

* Session creation
* Session validation
* Session expiration
* Session termination
* Session lookup

Authenticated clients will receive a session identifier.

The session identifier references session information stored and managed by the server.

Business modules and consumers must depend on the Session Service abstraction rather than any specific session implementation.

## Session Model

Conceptually:

```text
User
    ↓
Authentication
    ↓
Session Created
    ↓
Session Identifier
    ↓
Server Session Store
    ↓
Authenticated Requests
```

The client holds only a session identifier.

User identity, organization context, and session state remain under server control.

## Session Responsibilities

The Session Service is responsible for:

* Creating sessions after successful authentication.
* Validating sessions for incoming requests.
* Determining session expiration.
* Supporting logout functionality.
* Invalidating sessions when required.
* Maintaining authenticated user context.

The Session Service is not responsible for authorization decisions.

Authorization remains the responsibility of the Authorization Service.

## Session Timeout

Sessions must support expiration.

Examples include:

* Inactivity timeout
* Absolute timeout
* Administrative session termination

The exact timeout values are implementation concerns and may evolve over time.

Session expiration is considered a mandatory platform capability.

## Logout Strategy

Users must be able to terminate active sessions.

Logout invalidates the current session.

Once invalidated, the session can no longer be used to access protected resources.

Administrative session termination may be supported in future versions.

## Alternatives Considered

### Stateless JWT from Day One

Use JWT tokens as the primary session mechanism.

#### Rejected

JWT introduces additional complexity that is not required for the first platform iteration.

While JWT offers advantages in distributed environments, CFFP is initially designed as a modular monolith.

A server-side session model provides a simpler and more controllable starting point.

---

### External Identity Provider Session Management

Delegate all session management to an external identity provider.

#### Rejected

This introduces unnecessary dependencies and complexity before the platform has established a working core architecture.

External providers may be introduced later.

---

### Authentication Without Sessions

Require authentication for every request without maintaining authenticated state.

#### Rejected

This would create a poor user experience and unnecessary processing overhead.

Session management is required for practical platform operation.

## Consequences

### Positive

* Simple implementation.
* Centralized session control.
* Easy logout support.
* Easy session revocation.
* Straightforward timeout handling.
* Good fit for a modular monolith architecture.
* Supports future evolution.

### Negative

* Requires server-side session storage.
* Requires session lifecycle management.
* Slightly less suitable for highly distributed environments compared to stateless approaches.

These trade-offs are acceptable for the initial platform architecture.

## Future Evolution

The session implementation must remain replaceable.

Future implementations may include:

* JWT
* OAuth Access Tokens
* OpenID Connect
* Azure Active Directory
* SAML-based identity providers
* Distributed session architectures

The Session Service contract should remain stable while the underlying implementation evolves.

Consumers should not require modification when session implementations change.

## Relationship to Other Decisions

Session management is intentionally separated from authentication and authorization.

Authentication answers:

```text
Who is the user?
```

Session management answers:

```text
Is the user currently authenticated?
```

Authorization answers:

```text
What is the user allowed to do?
```

These responsibilities remain independent but work together within the overall security architecture.

## Overall Security Flow

```text
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

This sequence represents the agreed security architecture for CFFP.

## Related Decisions

* ADR-001 Authentication Strategy
* ADR-002 Authorization Strategy
* ADR-003 Role Model
* ADR-004 Permission Model
* ADR-005 Organization Isolation
