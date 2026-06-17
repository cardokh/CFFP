# CFFP Working Agreement

Version: 1.0

---

# 1. Purpose

This document defines how CFFP development should be performed.

The objective is to build CCore safely, consistently and efficiently while continuously improving both the platform and the way we develop it.

This document is intentionally a living agreement.

Whenever we discover a better way of working, this document should be updated before continuing development.

---

# 2. Core Principles

## 2.1 No Code Before Contract

Before implementation begins we must agree on:

- The problem being solved
- Success criteria
- Scope
- Out of scope
- Expected deliverables
- Validation approach

Implementation should never begin before a shared understanding has been reached.

---

## 2.2 User Experience Before API Design

For stories involving user interaction, the user experience is designed before backend implementation.

The workflow is:

1. Understand the user's goal.
2. Sketch or describe the UI.
3. Walk through the interaction.
4. Agree on the workflow.
5. Design the backend that supports the workflow.

The backend exists to support the user experience—not the other way around.

---

## 2.3 Architecture First

Implementation follows architecture.

Architecture does not follow implementation.

Architectural decisions should always be agreed before code generation begins.

---

## 2.4 Small End-to-End Vertical Slices

Development should proceed through small functional vertical slices.

Each slice should deliver something that works end-to-end and can be validated before continuing.

---

## 2.5 Test-Driven and Validation-First Development

Testing is part of development—not an activity performed afterwards.

Whenever practical:

- Write unit tests
- Validate individual components
- Test positive scenarios
- Test negative scenarios
- Test edge cases

Passing tests alone are insufficient.

The implementation must also satisfy the intended use case.

Long-term objective:

GUI Test Automation should become the primary validation mechanism for complete user workflows.

---

## 2.6 Automation First

Repeatable work should eventually become automated.

Every manual task should be considered a candidate for future automation.

The platform should continuously automate its own development workflow.

---

## 2.7 AI Output Is Untrusted

AI-generated artifacts must always be:

- Inspected
- Validated
- Tested
- Approved

Generated output should never be trusted simply because it compiles.

---

# 3. Working Interaction

This section defines how the human developer and the AI collaborate.

---

## 3.1 Conversation Is For Decisions

The conversation is used for:

- Analysis
- Design
- Architecture
- Discussion
- Reviews
- Decisions

Implementation should only begin after agreement has been reached.

---

## 3.2 Repository Is The Source Of Truth

The repository is always the authoritative source.

Conversation history must never replace the actual repository.

---

## 3.3 ZIP-Based Collaboration

The preferred collaboration model is based on ZIP archives.

Human responsibilities:

- Share the current repository (or relevant project) as a ZIP archive.
- Share the latest repository whenever significant implementation has been completed.

AI responsibilities:

- Inspect the ZIP archive before implementation.
- Generate complete implementation artifacts.
- Return generated artifacts as downloadable files or ZIP archives whenever practical.

Both participants should always work from the same repository version.

---

## 3.4 Avoid Manual Copy & Paste

Manual copy and paste should be considered an exception.

Acceptable:

- Small examples
- Architecture discussions
- Short snippets
- Documentation examples

Avoid whenever practical:

- Source code
- Multiple files
- Configuration
- Tests
- Project structures
- Documentation collections

Complete artifacts are preferred over partial snippets.

---

## 3.5 Whole-Artifact Preference

Whenever practical:

Generate complete files.

Avoid partial patches.

Avoid editing instructions.

Avoid manual merging.

Complete artifacts reduce ambiguity and improve review quality.

---

## 3.6 Explicit Approval Gates

Implementation pauses between major phases.

Approval is required before moving from:

- Discussion → Design
- Design → Implementation
- Implementation → Validation
- Validation → Git

Progression should never be assumed.

---

## 3.7 Repository Synchronisation

After implementation the repository becomes the new source of truth.

Future implementation should begin from the latest repository rather than from previous conversation history.

---

# 4. Story Lifecycle

Every story follows the same lifecycle.

## Phase 1 – Discussion

Understand the problem.

Outputs:

- Scope
- Constraints
- Assumptions
- User goals
- Acceptance criteria

No implementation.

---

## Phase 2 – User Workflow & UI

For stories involving a UI:

- Sketch the interface.
- Discuss the workflow.
- Validate the interaction.
- Agree on the user experience.

No backend implementation yet.

---

## Phase 3 – Technical Design

Agree on:

- Components
- APIs
- Data structures
- Configuration
- Validation strategy
- Testing strategy

---

## Phase 4 – Repository Inspection

Inspect:

- Project structure
- Existing code
- Existing patterns
- Existing tests
- Existing configuration

Never guess.

---

## Phase 5 – Implementation Planning

Define:

- Artifacts
- Dependencies
- Validation
- Testing
- Rollback

---

## Phase 6 – Artifact Generation

Prefer generating:

- Python automation
- JSON configuration
- Documentation
- Test suites
- Validation scripts

Automation is preferred over manual implementation whenever practical.

---

## Phase 7 – Validation

Validate generated artifacts.

Examples:

- Compile validation
- Static inspection
- Configuration validation
- Architecture inspection
- Hardcoded-path inspection

---

## Phase 8 – Testing

Testing should verify:

- Technical correctness
- Intended behaviour

Examples:

- Unit tests
- Integration tests
- Endpoint tests
- Regression tests

---

## Phase 9 – Human Approval

Questions:

- Does it solve the problem?
- Does it follow architecture?
- Is it maintainable?
- Is it tested?
- Is it documented?

Only approved work proceeds.

---

## Phase 10 – Git

Git is separate from implementation.

Only approved work should be committed.

Commits should reference the corresponding story.

---

# 5. Definition of Done

A story is Done when:

- Requirements are understood.
- User workflow is agreed.
- Technical design is complete.
- Repository has been inspected.
- Artifacts have been generated.
- Artifacts have been validated.
- Tests have passed.
- Intended behaviour has been verified.
- Human approval has been given.
- Documentation has been updated.
- Git commit has been completed where appropriate.

---

# 6. Roles & Responsibilities

## Human

Responsible for:

- Product vision
- Business decisions
- Architecture approval
- User experience approval
- Final acceptance
- Git decisions

## AI

Responsible for:

- Analysis
- Design support
- Repository inspection
- Artifact generation
- Validation support
- Documentation
- Risk identification

The AI assists.

The human makes the final decisions.

---

# 7. Continuous Improvement

This agreement is part of the CFFP project.

Whenever the workflow fails:

1. Identify the failure.
2. Understand why it happened.
3. Improve the workflow.
4. Update this document.
5. Continue development using the improved process.

The process itself is continuously developed alongside CCore.