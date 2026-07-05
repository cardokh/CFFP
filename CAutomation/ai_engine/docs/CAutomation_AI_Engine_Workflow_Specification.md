# CAutomation AI Engine Workflow Specification

Version: Draft 1  
Status: Review Draft  
Scope: CAutomation AI Engine workflow, pipeline responsibilities, artifact flow, and project-output contract  
Last Updated: July 2026

---

## 1. Purpose of This Document

This document describes the intended workflow for the CAutomation AI Engine.

The goal is to define, in detail, what the AI Engine is trying to achieve, how it should be structured, what each pipeline should consume, what each pipeline should generate, and where produced artifacts should live.

This document is intended to be reviewed by humans and by other AI models before the remaining pipelines are implemented. It should act as a shared architectural reference so that future implementation work does not drift from the agreed workflow.

This document is not an implementation guide for Python classes. It is a workflow and artifact-contract specification.

---

## 2. High-Level Goal

CAutomation is intended to automate parts of the software engineering lifecycle while preserving human control, traceability, validation, and approval.

The AI Engine should transform a manually described software project into increasingly structured engineering artifacts through a sequence of deterministic pipelines.

The intended flow is:

```text
Human-authored project documents
        ↓
Context Engineering
        ↓
Agile Artifact Generation
        ↓
Human review and approval
        ↓
Implementation planning and generation
        ↓
Validation
        ↓
Apply
        ↓
Verification
```

The AI Engine must not behave like an unconstrained coding assistant that reads arbitrary repository files and generates code directly from a conversation. Instead, it should operate on explicit inputs, produce explicit outputs, preserve provenance, and require validation and human approval at key gates.

---

## 3. Core Design Principles

### 3.1 Repository and Project Artifacts Are the Source of Truth

Conversation history must not be treated as authoritative.

The AI Engine should read from structured project input and previously generated approved artifacts. Each pipeline should consume declared artifacts and produce declared artifacts.

### 3.2 Context Engineering Before Generation

The AI model should not generate implementation artifacts from vague or incomplete context.

Before planning or generation, the system must create a curated context package from human-authored documents and project configuration.

### 3.3 Provenance Must Be Preserved

Every important generated artifact should be traceable back to its inputs.

The workflow should preserve:

- human-authored intent,
- architectural constraints,
- generated context packages,
- generated Agile artifacts,
- approvals,
- generated implementation artifacts,
- validation results,
- applied changes.

### 3.4 Pipelines Have One Clear Responsibility

Each pipeline must have a focused responsibility.

A pipeline should not perform work that belongs to a later stage. For example, the Agile artifact pipeline should not generate database metadata, backend files, frontend plans, or implementation specifications. Those belong to later implementation-oriented stages.

### 3.5 Human Approval Gates Are Part of the Workflow

Some artifacts must be reviewed and approved before downstream pipelines are allowed to use them.

The most important early approval gate is after Agile artifacts have been generated.

### 3.6 AI Output Is Untrusted Until Validated

AI-generated artifacts must be validated, inspected, and approved before they are treated as authoritative input for later stages.

---

## 4. Manual Input Model

The workflow begins with manually created documents.

The first version of the workflow is based on two primary human-authored documents:

```text
WHAT document
HOW document
```

These documents are created before the AI Engine generates downstream artifacts.

### 4.1 WHAT Document

The WHAT document describes what should be built.

It focuses on product intent, business functionality, user goals, scope, and expected outcomes.

Typical content includes:

- product or module purpose,
- business goals,
- user goals,
- functional requirements,
- major workflows,
- important use cases,
- constraints from the product perspective,
- out-of-scope items,
- success criteria.

The WHAT document should not primarily describe implementation technology. Its purpose is to define the functional and product-level intent.

### 4.2 HOW Document

The HOW document describes how the product should be implemented.

It focuses on technical direction, architecture, implementation constraints, technology choices, standards, and engineering expectations.

Typical content includes:

- architecture principles,
- selected technology stack,
- backend approach,
- frontend approach,
- database approach,
- API conventions,
- security principles,
- coding standards,
- testing expectations,
- validation rules,
- deployment constraints,
- non-functional requirements.

The HOW document should not replace the WHAT document. It constrains and guides implementation of the functionality described in the WHAT document.

### 4.3 Supporting Input Documents

The workflow may also allow supporting input documents, such as:

- ADRs,
- style guides,
- domain notes,
- existing project summaries,
- module-specific notes,
- UX notes,
- validation rules,
- external constraints.

Supporting documents must be explicitly selected and included. The AI Engine should not read arbitrary repository content unless a pipeline contract allows it.

---

## 5. Project Artifact Location Model

The AI Engine lives under:

```text
CAutomation/ai_engine/
```

Project-specific inputs and generated project artifacts live under:

```text
CAutomation/projects/<project_id>/
```

For the current reference project:

```text
CAutomation/projects/cffp/
```

The AI Engine pipeline folders contain reusable pipeline definitions, tasks, configuration, and runtime logic. They are not the primary location for project-specific generated artifacts.

Pipeline execution reports may exist under pipeline runtime output folders, but durable project artifacts should be written under the relevant project folder.

---

## 6. Initial Project Folder Sketch

A project folder should support a staged artifact flow.

A conceptual project structure is:

```text
CAutomation/
└── projects/
    └── cffp/
        ├── project.json
        ├── input/
        │   ├── client/
        │   ├── engineering/
        │   └── modules/
        │
        ├── context/
        │   ├── current/
        │   └── history/
        │
        ├── agile/
        │   ├── current/
        │   ├── approved/
        │   └── history/
        │
        ├── implementation/
        │   ├── current/
        │   ├── approved/
        │   └── history/
        │
        ├── generation/
        │   ├── current/
        │   └── history/
        │
        ├── validation/
        │   ├── current/
        │   └── history/
        │
        ├── apply/
        │   ├── current/
        │   └── history/
        │
        └── verification/
            ├── current/
            └── history/
```

This is a conceptual target model. The existing implementation may introduce these folders incrementally.

---

## 7. Pipeline Overview

The intended pipeline sequence is:

```text
01_context_engineering
02_agile_artifact_generation
03_implementation_planning
04_generation
05_validation
06_apply
07_verification
```

The existing repository currently has numbered pipeline folders. The exact folder names may evolve, but the responsibility boundaries in this document should remain clear.

The most important correction is that Agile artifact generation and implementation planning are separate stages.

---

## 8. Pipeline 01: Context Engineering

### 8.1 Purpose

Pipeline 01 creates a curated context package from manually authored project documents.

It answers:

```text
What do we know, and what context is safe and relevant for downstream AI-assisted work?
```

### 8.2 Inputs

Primary inputs:

- WHAT document,
- HOW document,
- project configuration,
- selected supporting documents.

Possible input location:

```text
CAutomation/projects/cffp/input/
```

### 8.3 Outputs

Pipeline 01 should generate a durable context package under the project folder.

Possible output location:

```text
CAutomation/projects/cffp/context/current/
```

Expected artifacts may include:

```text
context_package.json
context_package.md
context_manifest.json
context_sources.json
context_validation_report.json
context_summary.md
```

### 8.4 Responsibilities

Pipeline 01 should:

- validate required manual input documents,
- extract relevant content from selected documents,
- preserve source provenance,
- separate functional intent from technical constraints,
- build a curated context package,
- validate the context package,
- write execution and validation reports.

### 8.5 Non-Responsibilities

Pipeline 01 should not:

- create Agile artifacts,
- create user stories,
- create implementation plans,
- generate code,
- generate database metadata,
- generate frontend/backend artifacts.

---

## 9. Pipeline 02: Agile Artifact Generation

### 9.1 Purpose

Pipeline 02 generates Agile planning artifacts from the approved or current context package.

It answers:

```text
What work needs to be done from a product and delivery perspective?
```

This pipeline is about project planning, not technical implementation planning.

### 9.2 Inputs

Primary inputs:

- context package from Pipeline 01,
- project metadata,
- module metadata if applicable,
- optional Agile configuration rules.

Possible input location:

```text
CAutomation/projects/cffp/context/current/
```

### 9.3 Outputs

Pipeline 02 should generate Agile artifacts under the project folder.

Possible output location:

```text
CAutomation/projects/cffp/agile/current/
```

Expected artifacts may include:

```text
epics.json
epics.md
features.json
features.md
user_stories.json
user_stories.md
technical_stories.json
technical_stories.md
tasks.json
tasks.md
acceptance_criteria.json
acceptance_criteria.md
dependencies.json
priorities.json
agile_traceability_matrix.json
agile_generation_report.json
agile_validation_report.json
agile_summary.md
```

### 9.4 Responsibilities

Pipeline 02 should:

- read the curated context package,
- identify product-level work items,
- generate epics,
- generate features,
- generate user stories,
- generate technical stories where appropriate,
- generate tasks,
- generate acceptance criteria,
- define dependencies between Agile artifacts,
- preserve traceability back to context sources,
- validate completeness and consistency of Agile artifacts.

### 9.5 Non-Responsibilities

Pipeline 02 should not:

- generate database metadata,
- generate backend implementation plans,
- generate frontend implementation plans,
- generate API specifications,
- generate code,
- decide final implementation details,
- apply changes to the repository.

Those responsibilities belong to later implementation-oriented pipelines.

### 9.6 Human Approval Gate

Pipeline 02 must be followed by human review and approval.

Before downstream implementation work begins, the generated Agile artifacts should be reviewed, corrected if needed, and approved.

Approved Agile artifacts may be copied or promoted to:

```text
CAutomation/projects/cffp/agile/approved/
```

Downstream implementation pipelines should consume approved Agile artifacts, not unreviewed draft artifacts.

---

## 10. Pipeline 03: Implementation Planning

### 10.1 Purpose

Pipeline 03 converts approved Agile artifacts into technical implementation plans.

It answers:

```text
How should each approved story be implemented?
```

This is the first stage where implementation-specific artifacts such as database metadata, API plans, backend plans, frontend plans, and test plans should be produced.

### 10.2 Inputs

Primary inputs:

- approved Agile artifacts,
- context package,
- HOW document constraints through the context package,
- project/module configuration,
- implementation standards.

Possible input locations:

```text
CAutomation/projects/cffp/agile/approved/
CAutomation/projects/cffp/context/current/
```

### 10.3 Outputs

Possible output location:

```text
CAutomation/projects/cffp/implementation/current/
```

Expected artifacts may include:

```text
implementation_plan.json
implementation_plan.md
story_implementation_map.json
artifact_manifest.json
dependency_graph.json
generation_order.json
traceability_matrix.json
```

Implementation planning may also produce target-specific planning artifacts, such as:

```text
database_metadata.json
database_schema_plan.json
entity_model_plan.json
api_plan.json
backend_plan.json
frontend_plan.json
test_plan.json
deployment_plan.json
```

### 10.4 Responsibilities

Pipeline 03 should:

- consume approved Agile artifacts,
- determine implementation units per story,
- map stories to technical artifacts,
- identify database changes,
- identify API requirements,
- identify backend components,
- identify frontend components,
- identify tests and validation requirements,
- define generation order,
- define dependencies,
- produce a machine-readable implementation plan for generation.

### 10.5 Non-Responsibilities

Pipeline 03 should not:

- generate final source code,
- apply repository changes,
- validate compiled/generated code,
- bypass human-approved Agile artifacts.

---

## 11. Pipeline 04: Generation

### 11.1 Purpose

Pipeline 04 generates implementation artifacts from the approved implementation plan.

It answers:

```text
What files and artifacts should be generated to implement the approved plan?
```

### 11.2 Inputs

Primary inputs:

- implementation plan,
- artifact manifest,
- generation order,
- context package,
- approved Agile artifacts where needed for traceability.

Possible input locations:

```text
CAutomation/projects/cffp/implementation/approved/
CAutomation/projects/cffp/context/current/
CAutomation/projects/cffp/agile/approved/
```

### 11.3 Outputs

Possible output location:

```text
CAutomation/projects/cffp/generation/current/
```

Expected artifacts may include:

```text
generated_artifact_manifest.json
generation_report.json
generation_traceability_matrix.json
staging/
```

The staging folder may contain generated files before they are validated and applied.

### 11.4 Generation Targets

Generation may be organized by target area:

```text
database
backend
frontend
testing
deployment
```

These are generation targets inside the Generation stage. They should not be confused with lifecycle pipelines.

### 11.5 Non-Responsibilities

Pipeline 04 should not:

- invent unapproved stories,
- rewrite Agile scope,
- apply generated files directly to the live repository,
- mark generated output as trusted without validation.

---

## 12. Pipeline 05: Validation

### 12.1 Purpose

Pipeline 05 validates generated artifacts before they are applied.

It answers:

```text
Are the generated artifacts correct, complete, safe, and consistent with the approved inputs?
```

### 12.2 Inputs

Primary inputs:

- generated artifacts,
- generated artifact manifest,
- implementation plan,
- approved Agile artifacts,
- context package,
- validation rules.

### 12.3 Outputs

Possible output location:

```text
CAutomation/projects/cffp/validation/current/
```

Expected artifacts may include:

```text
validation_report.json
validation_summary.md
issue_report.json
traceability_validation_report.json
architecture_validation_report.json
test_execution_report.json
```

### 12.4 Responsibilities

Pipeline 05 should validate:

- file completeness,
- manifest consistency,
- traceability to approved Agile artifacts,
- conformance to HOW constraints,
- architectural consistency,
- coding standards where practical,
- tests where practical,
- safety of applying changes.

### 12.5 Non-Responsibilities

Pipeline 05 should not:

- apply changes to the live repository,
- silently fix generated artifacts without recording provenance,
- approve its own output without human review where approval is required.

---

## 13. Pipeline 06: Apply

### 13.1 Purpose

Pipeline 06 applies validated generated artifacts to the target repository or target project location.

It answers:

```text
Which validated artifacts should be moved into the actual project, and how should that be recorded?
```

### 13.2 Inputs

Primary inputs:

- validated generated artifacts,
- validation report,
- generated artifact manifest,
- apply configuration,
- human approval if required.

### 13.3 Outputs

Possible output location:

```text
CAutomation/projects/cffp/apply/current/
```

Expected artifacts may include:

```text
apply_report.json
applied_artifact_manifest.json
backup_manifest.json
change_summary.md
```

### 13.4 Responsibilities

Pipeline 06 should:

- apply only validated artifacts,
- respect allowed target paths,
- preserve backups or change records where appropriate,
- record exactly what changed,
- produce an apply report.

### 13.5 Non-Responsibilities

Pipeline 06 should not:

- generate new implementation artifacts,
- bypass validation,
- apply files outside approved scope.

---

## 14. Pipeline 07: Verification

### 14.1 Purpose

Pipeline 07 verifies the repository after changes have been applied.

It answers:

```text
Does the actual repository still work after the applied changes?
```

### 14.2 Inputs

Primary inputs:

- applied repository state,
- apply report,
- validation rules,
- test configuration,
- approved Agile artifacts and implementation plan for traceability.

### 14.3 Outputs

Possible output location:

```text
CAutomation/projects/cffp/verification/current/
```

Expected artifacts may include:

```text
verification_report.json
verification_summary.md
post_apply_test_report.json
regression_report.json
```

### 14.4 Responsibilities

Pipeline 07 should:

- run post-apply checks,
- verify expected files exist,
- run tests where practical,
- verify story-level acceptance criteria where practical,
- report failures clearly,
- preserve traceability from applied changes back to approved artifacts.

---

## 15. Approval Gates

The workflow should support explicit approval gates.

Recommended gates:

```text
After Pipeline 01: approve context package if needed
After Pipeline 02: approve Agile artifacts
After Pipeline 03: approve implementation plan if needed
After Pipeline 05: approve validated generated artifacts before apply
After Pipeline 07: accept or reject completed implementation
```

The most important early gate is after Pipeline 02, because generated Agile artifacts define the work that later implementation pipelines will execute.

---

## 16. Artifact Traceability

Each downstream artifact should be traceable to upstream artifacts.

Example traceability chain:

```text
WHAT/HOW document section
        ↓
context package item
        ↓
epic
        ↓
feature
        ↓
user story
        ↓
task
        ↓
implementation plan item
        ↓
generated artifact
        ↓
validation result
        ↓
applied file
        ↓
verification result
```

Traceability is a core part of the architecture. It allows humans and tools to audit why a file was generated and which approved requirement it supports.

---

## 17. Pipeline Runtime Model

The AI Engine uses reusable runtime infrastructure.

The current direction is:

```text
CAutomation/ai_engine/runtime/
```

This runtime contains shared execution support for pipelines and tasks.

The runtime should support:

- configuration-driven pipeline execution,
- task registry resolution,
- task instance execution,
- task reporting,
- pipeline reporting,
- execution history,
- current-run management,
- shared path helpers,
- deterministic artifact paths.

Pipelines should be orchestrators only. They should execute reusable task definitions through configured task instances.

Tasks should be independently executable and should produce their own reports.

The orchestrator should aggregate task reports into a pipeline execution report.

---

## 18. Pipeline Folder Model

Pipeline definitions live under:

```text
CAutomation/ai_engine/pipelines/
```

Conceptual lifecycle folders:

```text
00_shared/
01_context_engineering/
02_agile_artifact_generation/
03_implementation_planning/
04_generation/
05_validation/
06_apply/
07_verification/
```

The exact numbering and folder names may be adjusted incrementally. However, the responsibility boundaries should remain explicit.

### 18.1 00_shared

`00_shared` should contain pipeline-level shared templates, task definitions, schemas, examples, or reusable resources when they are proven to be shared across multiple pipelines.

It should not replace the engine runtime.

### 18.2 runtime

`runtime` contains executable shared framework code used by the AI Engine.

The distinction is:

```text
runtime    = shared engine execution code
00_shared  = shared pipeline resources/templates/configuration patterns
```

---

## 19. Important Boundary: Agile Planning vs Implementation Planning

This boundary is critical.

Agile Artifact Generation produces:

```text
epics
features
user stories
tasks
acceptance criteria
dependencies
priorities
```

Implementation Planning produces:

```text
database metadata
API plans
backend plans
frontend plans
test plans
artifact manifests
generation order
```

These must not be mixed.

The Agile pipeline defines the work. The Implementation Planning pipeline defines how the approved work should be implemented.

---

## 20. Expected Review Questions for External AI Models

This document should be given to other AI models for review and audit.

Suggested review questions:

1. Is the pipeline sequence logically sound?
2. Are the boundaries between Context Engineering, Agile Artifact Generation, Implementation Planning, Generation, Validation, Apply, and Verification clear?
3. Is anything important missing between Agile approval and code generation?
4. Are any pipelines doing too much?
5. Are any pipelines unnecessary or should any be split?
6. Are the proposed artifacts sufficient for traceability?
7. Is the separation between project artifacts and pipeline runtime artifacts clear?
8. Are the approval gates in the right places?
9. Does the workflow support deterministic AI-assisted software engineering?
10. What risks or inconsistencies should be addressed before implementing Pipeline 02?

---

## 21. Current Implementation Position

At the time this document is drafted, Pipeline 01 is the reference implementation.

The framework already supports the following architectural ideas:

- configuration-driven pipelines,
- pipelines as orchestrators,
- reusable task definitions,
- task registry resolution,
- independently executable tasks,
- task-level reports,
- pipeline-level execution reports,
- execution history,
- current run and archived executions,
- shared task runtime,
- shared pipeline runtime,
- shared path helpers.

The next major workflow decision should be made before implementing further pipelines.

Pipeline 02 should not be implemented until the responsibility boundary is confirmed:

```text
Pipeline 02 = Agile Artifact Generation only
```

---

## 22. Summary

CAutomation should not jump directly from context engineering to code generation.

The intended workflow is staged:

```text
Manual WHAT/HOW documents
        ↓
Context Package
        ↓
Agile Artifacts
        ↓
Human Approval
        ↓
Implementation Plan
        ↓
Generated Artifacts
        ↓
Validation
        ↓
Apply
        ↓
Verification
```

This separation is the foundation of the CAutomation AI Engine.

It allows the project to preserve provenance, maintain human control, validate AI output, and build software through a repeatable pipeline-based workflow rather than through unstructured prompting.
