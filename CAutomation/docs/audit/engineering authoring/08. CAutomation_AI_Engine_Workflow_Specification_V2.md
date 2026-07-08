# CAutomation AI Engine Workflow Specification

Version: 2.0  
Status: Final Contract Candidate  
Scope: CAutomation AI Engine workflow, execution architecture, pipeline responsibilities, task architecture, artifact flow, project-management publishing, approval gates, and verification model  
Reference Project: CAutomation  
Last Updated: July 2026  
Supersedes: Draft 5 / Version 1 review draft

---

## 1. Executive Summary

**CAutomation is a generic AI-assisted software engineering framework.**

Its purpose is to transform a small set of manually authored project specifications into a complete, deliverable web application through deterministic, project-specific automation pipelines. The framework does not treat AI as a one-shot code generator. Instead, it uses AI as part of a structured engineering workflow where every stage has explicit inputs, explicit outputs, validation, traceability, execution reports, and human approval gates.

The current reference project is **CAutomation**. CAutomation is treated as a realistic multi-module web application used to validate the AI Engine workflow. The initial reference modules are:

```text
Pipeline Management
User & Client Management
```

The intended end-to-end workflow is:

```text
Reference Project: CAutomation
│
├── Project-level WHAT/HOW contracts
├── Module-level SRS/ATS contracts
└── Explicitly selected supporting documents
        ↓
01 Context Engineering
        ↓
Context Package
        ↓
02 Planning
        ↓
Agile Planning Package
Technical Implementation Planning Package
        ↓
03 Project Management Publishing
        ↓
Published/synchronized project-management work items
Human approval gate
        ↓
04 Generation
        ↓
Story-oriented, test-first implementation artifacts in staging
        ↓
05 Validation
        ↓
Validated generated artifacts
        ↓
06 Apply
        ↓
Applied repository/project changes
        ↓
07 Verification
        ↓
Verified deliverable web application
```

The most important architectural rules are:

- Pipeline 01 is the only pipeline that consumes manually authored requirement and architecture documents directly.
- Pipeline 02 produces both the Agile Planning Package and the Technical Implementation Planning Package.
- Pipeline 03 publishes or synchronizes Agile planning artifacts to a configured project-management target without generating implementation code.
- Pipeline 04 generates implementation artifacts story by story using a test-first workflow.
- Pipeline 05 validates generated artifacts and must not modify them.
- Pipeline 06 applies only validated artifacts.
- Pipeline 07 verifies the final repository/application outcome.

This document is the architectural workflow contract for AI Engine implementation.

---

## 2. Purpose of This Document

This document describes the intended workflow for the **CAutomation AI Engine**.

It defines:

- what the AI Engine is trying to achieve,
- how the workflow is structured,
- how pipelines and tasks are organized,
- what each pipeline consumes,
- what each pipeline generates,
- how project-management publishing fits into the workflow,
- where approval gates exist,
- how task and pipeline execution must be reported,
- how generated artifacts remain traceable and deterministic.

This is not a Python implementation guide. It is a workflow, artifact, task, pipeline, and execution-contract specification.

---


## 2A. Version 2 Contract Completion Baseline

Version 2 completes the architectural review cycle for the AI Engine workflow and incorporates the approved findings from the independent Gemini audit and the subsequent architecture-board decisions.

This version does not broaden the product scope. It tightens execution determinism, closes ambiguity around the transition from Planning to Generation, formalizes shared frontend and reporting contracts, and defines controlled exceptions to tenant filtering for authenticated platform-level operations.

The following Version 2 improvements are normative:

- the seven-pipeline architecture is the authoritative AI Engine workflow;
- Pipeline 03 produces an immutable Planning Freeze / Generation Baseline before Pipeline 04 may execute;
- Pipeline 04 consumes the frozen baseline, not a mutable external project-management backlog;
- background execution resilience is handled through persisted execution state and startup reconciliation, without introducing Celery, Redis, or other external task brokers;
- platform-level repository bypass is permitted only through an explicit, audited, authorization-checked bypass contract;
- the frontend architecture must use a shared session, client, and project context contract rather than inventing per-screen state flows;
- execution and validation reports must expose common metadata fields to support unified rendering and traceability;
- shared functionality must be promoted from task-owned code to pipeline shared code or AI Engine shared libraries when reuse criteria are met;
- lifecycle status values are domain-specific unless explicitly declared as shared enumerations.

Future architectural changes after this version is frozen must be handled as controlled change requests against this specification rather than silent implementation drift.
## 3. Background and Inspiration

The CAutomation AI Engine is inspired by professional-grade AI-assisted coding approaches that emphasize context engineering, provenance preservation, structured artifacts, focused context sessions, staged software engineering work, and validation before trust.

CAutomation does not implement BMAD, Spec Kit, or any other methodology directly. It defines its own workflow, artifact model, approval gates, pipeline contracts, task execution standards, and verification model.

The core idea is:

> CAutomation should not simply ask an AI model to generate code. It should automate a structured software engineering process.

The AI Engine transforms manually authored project specifications into increasingly concrete engineering artifacts through deterministic pipelines. Each pipeline has explicit inputs, explicit outputs, validation, traceability, and human approval gates where required.

---

## 4. Vision

The long-term vision is to create software that can be given a small set of manually authored project documents and then use AI-assisted software engineering to progressively produce the artifacts required to deliver an end-to-end web application.

The intended final result is not only source code. The complete result should include:

- normalized project and module contracts,
- context packages,
- Agile planning artifacts,
- project-management publishing artifacts,
- implementation plans,
- database metadata,
- database schema artifacts,
- backend source code,
- API artifacts,
- frontend source code,
- tests,
- validation reports,
- apply reports,
- verification reports,
- traceability records.

The AI Engine should be reusable across projects. The current reference project is **CAutomation**, a realistic multi-module web application used to validate the framework and demonstrate the complete workflow.

---

## 5. Reference Project: CAutomation

CAutomation is the canonical reference project used to design, validate, and prove the AI Engine. It must be treated as a realistic multi-module web application, not as a single standalone module.

The project is:

```text
CAutomation
```

The initial reference modules are:

```text
Pipeline Management
User & Client Management
```

Project-level contracts describe the CAutomation platform as a whole, including business objectives, platform architecture, global engineering principles, technology stack, security principles, quality requirements, cross-module rules, and client/platform concepts.

Module-level contracts describe only an individual module. Each active module has two manually authored module contracts:

```text
WHAT/SRS document
HOW/ATS document
```

These module contracts are authoritative only for that module. They do not replace project-level contracts.

The existence of more than one reference module is intentional. It proves that the AI Engine is project-aware and module-agnostic: the same configured pipelines and task implementations must process multiple modules through configuration, without code changes per module.

---

## 6. AI Engine Execution Architecture

This section defines the common architecture that every pipeline and every task must follow.

### 6.1 Project-Specific Pipeline Execution

Every pipeline execution is project-specific.

A pipeline runs within exactly one configured project context, for example:

```text
projects/CAutomation/
```

The project configuration defines the project identity, enabled modules, contract locations, output locations, approval state, and execution context.

Pipelines must not operate on undeclared projects or undeclared modules.

### 6.2 Module-Agnostic Pipeline and Task Implementation

Pipeline and task implementations must be module-agnostic.

Adding or updating a module must require configuration changes only, not code changes inside the task implementation.

For the CAutomation reference project, the same Pipeline 01 task implementations must be able to normalize, extract, validate, and package both:

```text
Pipeline Management
User & Client Management
```

without module-specific code branches.

### 6.3 Configuration Hierarchy

The AI Engine uses a three-level configuration hierarchy:

```text
Project Configuration
        ↓
Pipeline Configuration
        ↓
Task Configuration
```

Project configuration defines the active project and enabled modules.

Pipeline configuration defines orchestration: pipeline identity, task sequence, required upstream artifacts, output locations, approval requirements, and shared runtime context.

Task configuration defines task-specific execution: task inputs, task outputs, validation rules, parser settings, profile settings, task failure behavior, and report paths.

A task must read its own task configuration file. A task must not depend on hidden pipeline-only configuration for its internal behavior.

### 6.4 Pipeline and Task Self-Containment

Each pipeline orchestrates reusable tasks.

Each task must be:

- self-contained,
- independently executable,
- independently testable,
- independently configurable,
- reusable where appropriate,
- responsible for its own execution report.

A task must expose a stable input/output contract and must not require the full pipeline to be running in order to be tested.

### 6.5 Execution Entry Point Standard

Every pipeline must contain:

```text
run_pipeline.py
run_pipeline_tests.py
```

`run_pipeline.py` is the standard entry point for executing one pipeline. It must load configuration, perform preflight validation, execute the configured task sequence, aggregate task results, and write a pipeline execution report.

`run_pipeline_tests.py` is the standard entry point for testing one pipeline. It must run pipeline-level tests, execute task test suites where configured, aggregate test reports, and return a deterministic pass/fail result.

Every task must contain:

```text
run_task.py
run_task_tests.py
```

`run_task.py` is the standard entry point for executing one task. It must load the task configuration, perform task preflight validation, execute the task, and write a task execution report.

`run_task_tests.py` is the standard entry point for testing one task. It must run the task's unit, integration, functional, and validation tests and produce a task test report.

### 6.6 Task Testing Architecture

Every task must include a test folder from the moment the task is created:

```text
tests/
├── unit/
├── integration/
├── functional/
└── validation/
```

Unit tests verify internal logic in isolation.

Integration tests verify integration with configuration, filesystem, shared components, and adjacent runtime services.

Functional tests verify that the task performs its documented responsibility.

Validation tests verify that the task enforces its validation rules, fails cleanly, and produces correct reports.

A task is not complete until its required tests pass.

### 6.7 Pipeline Preflight Contract

Every pipeline must begin with preflight validation.

Pipeline preflight must validate:

- project identity,
- pipeline identity,
- execution id,
- pipeline configuration,
- configured task sequence,
- task configuration references,
- required upstream artifacts,
- required approval state,
- output directory availability,
- report directory availability.

If preflight fails:

- no business processing tasks execute,
- no downstream artifacts are generated,
- a structured pipeline failure report is written,
- the pipeline exits with failed status.

### 6.8 Task Preflight Contract

Every task must begin with task preflight validation.

Task preflight must validate:

- task configuration file,
- required task inputs,
- required upstream artifact references,
- output paths,
- validation rules,
- task-specific settings.

If task preflight fails, the task must fail cleanly, write a task execution report, and return a failed status to the pipeline orchestrator.

### 6.9 Pipeline Artifact Dependency Rule

Each pipeline must consume only the approved artifacts produced by the immediately preceding pipeline, unless this specification explicitly states otherwise.

Pipelines must not:

- bypass intermediate pipelines,
- read raw source documents after normalized/context artifacts exist,
- read internal files from later pipelines,
- communicate through hidden in-memory state,
- depend on undocumented files.

The pipeline chain is:

```text
01 Context Engineering
    ↓ approved Context Package
02 Planning
    ↓ approved Planning Packages
03 Project Management Publishing
    ↓ publishing report and approval state
04 Generation
    ↓ generated staged artifacts
05 Validation
    ↓ validated artifact set
06 Apply
    ↓ applied repository state
07 Verification
```

### 6.10 Execution Transparency Contract

Every pipeline and every task must produce structured execution reports.

A pipeline execution report must include:

- pipeline_id,
- project_id,
- execution_id,
- started_at,
- finished_at,
- status,
- pipeline_config_path,
- resolved_task_sequence,
- task_config_paths,
- required_input_artifacts,
- resolved_input_artifacts,
- produced_output_artifacts,
- task_results,
- approval_state,
- errors,
- warnings,
- report_paths.

A task execution report must include:

- task_id,
- pipeline_id,
- project_id,
- execution_id,
- started_at,
- finished_at,
- status,
- task_config_path,
- input_artifacts,
- output_artifacts,
- validation_checks,
- parameters_used,
- errors,
- warnings,
- traceability_links.

### 6.11 Divide and Conquer Principle

The AI Engine must be designed using the Divide and Conquer principle.

Each task shall have a single, well-defined responsibility. A task should orchestrate small internal components rather than contain large, monolithic business logic files.

Task logic should be decomposed into components such as:

```text
Configuration Loader
Input Validator
Document Loader
Parser
Normalizer
Business Rule Engine
Output Writer
Report Generator
```

The intent is not to enforce an arbitrary line count. The intent is to prevent a task from becoming responsible for unrelated concerns.

### 6.12 Shared Component Architecture

The AI Engine shall maximize reuse by extracting common functionality into shared components rather than duplicating implementation across tasks or pipelines.

Reusable components exist at three levels:

```text
Task-owned components
Pipeline shared components
AI Engine-wide shared components
```

The promotion rule is:

- Used by one task: keep it inside that task.
- Used by multiple tasks in one pipeline: move it to the pipeline shared folder.
- Used by multiple pipelines: move it to the AI Engine shared library.

The global shared library is represented by:

```text
00_shared/
```

Duplication of business logic across tasks or pipelines is prohibited when a shared component is appropriate.

---


### 6.13 Shared Component Promotion Governance

The promotion rules in Section 6.12 are mandatory implementation governance, not optional refactoring guidance.

A reusable capability must remain at the narrowest level that satisfies current reuse requirements:

```text
One task only                     -> task-owned component
Multiple tasks in one pipeline    -> pipeline shared component
Multiple pipelines                -> AI Engine shared component
```

The following promotion triggers apply:

- if the same logic is needed by two or more tasks in the same pipeline, it becomes a pipeline shared candidate;
- if the same logic is needed by two or more pipelines, it becomes an AI Engine shared candidate;
- if duplicated logic reaches three independent usages, promotion is mandatory unless a documented exception is approved;
- exceptions must be captured in the relevant execution or design report and must identify the owning pipeline, affected tasks, reason for temporary duplication, and planned removal point.

Shared-component promotion must preserve deterministic behavior. Promotion must not introduce hidden runtime coupling, undeclared configuration dependencies, or cross-project state.

### 6.14 Domain-Specific Enumeration Rule

Lifecycle status values are domain-specific unless explicitly declared as shared enumerations in a project-level or AI Engine-wide contract.

For example:

```text
membership_status: Active, Suspended, Archived
pipeline_task_status: Active, Disabled, Archived
```

These are not automatically equivalent. Similar label names across modules do not imply shared behavior, shared validation logic, or shared interception rules. If a status set is intended to be shared, the owning contract must explicitly define the shared enumeration name, values, semantics, allowed transitions, and consumers.
## 7. End-to-End Workflow

The high-level workflow is:

```text
Human-authored project and module contracts
        ↓
01 Context Engineering
        ↓
Context Package
        ↓
02 Planning
        ↓
Agile Planning Package
Technical Implementation Planning Package
        ↓
03 Project Management Publishing
        ↓
Published or exported project-management artifacts
Human Approval
        ↓
04 Generation
        ↓
Generated implementation artifacts in staging
        ↓
05 Validation
        ↓
Validated generated artifacts
        ↓
06 Apply
        ↓
Applied repository/project changes
        ↓
07 Verification
        ↓
Verified deliverable web application
```

The Planning pipeline is responsible for architectural decomposition. The Generation pipeline is responsible for deterministic implementation.

If Generation must guess what to build, that is a Planning defect.

---

## 8. Core Design Principles

### 8.1 Automate Software Engineering, Not Prompting

CAutomation automates a staged engineering workflow. It must not behave like an unconstrained coding assistant.

### 8.2 Project Artifacts Are the Source of Truth

Conversation history is not authoritative. Pipelines consume declared artifacts and produce declared artifacts.

### 8.3 Context Engineering Comes First

The AI model must not generate planning or implementation artifacts from vague context. The first stage creates a curated Context Package from human-authored inputs.

### 8.4 Planning Before Generation

The Planning pipeline must generate both Agile planning artifacts and technical implementation planning artifacts before Generation begins.

### 8.5 Project Management Publishing Before Generation

The Agile Planning Package must be published, exported, or synchronized through the Project Management Publishing pipeline before Generation begins, unless explicitly disabled by configuration.

### 8.6 Provenance Must Be Preserved

Every important generated artifact must be traceable back to its inputs.

### 8.7 Pipelines Have One Clear Responsibility

Each pipeline must do one kind of work. A pipeline must not perform work that belongs to a later stage.

### 8.8 Human Approval Gates Are Part of the Workflow

Generated outputs are not automatically trusted. Important artifacts must be reviewed and approved before downstream pipelines consume them.

### 8.9 AI Output Is Untrusted Until Validated

AI-generated artifacts must be validated, inspected, and approved before they become authoritative inputs for later stages.

---

## 9. Pipeline Contract Overview

| Pipeline | Purpose | Primary Inputs | Primary Outputs | Approval Gate |
|---|---|---|---|---|
| 01 Context Engineering | Build trusted AI context from human-authored project inputs | Project/module contracts and selected supporting documents | Normalized input, Context Package, context manifest, source traceability | Optional context approval |
| 02 Planning | Convert the Context Package into complete planning packages | Approved Context Package | Agile Planning Package, Technical Implementation Planning Package, planning manifest, dependency graph, generation order | Required or recommended planning approval |
| 03 Project Management Publishing | Publish or synchronize Agile planning artifacts | Approved Agile Planning Package | Publishing report, external identifier map, publication manifest, updated traceability | Required before Generation |
| 04 Generation | Generate implementation artifacts story by story | Approved Technical Implementation Planning Package, approved Agile Planning Package, approval state | Generated files in staging, generated artifact manifest, generation report | No direct trust; must go to Validation |
| 05 Validation | Validate generated artifacts before Apply | Generated artifacts, manifests, plans, tests, traceability | Validation report, issue report, apply readiness report | Required before Apply |
| 06 Apply | Apply validated artifacts to the target repository | Validated artifacts, apply config, approval | Applied files, apply report, change summary, applied artifact manifest | Approval required before or during Apply depending on mode |
| 07 Verification | Verify the project after Apply | Applied state, apply report, tests, acceptance criteria | Verification report, final certification report | Final acceptance |

---

## 10. Project Artifact Location Model

The AI Engine runtime and pipeline definitions live under:

```text
CAutomation/ai_engine/
```

Project-specific inputs and generated project artifacts live under:

```text
CAutomation/projects/<project_id>/
```

For the reference project:

```text
CAutomation/projects/CAutomation/
```

Pipeline folders contain reusable pipeline definitions, tasks, configuration, and runtime logic. They are not the primary location for durable project artifacts.

Durable project artifacts must be written under the relevant project folder.

---

## 11. Reference Project Folder Sketch

The canonical reference project folder is:

```text
CAutomation/
└── projects/
    └── CAutomation/
        ├── project.json
        ├── input/
        │   ├── project/
        │   │   └── contracts/
        │   └── modules/
        │       ├── pipeline_management/
        │       └── user_client_management/
        ├── normalized_input/
        ├── context/
        ├── planning/
        │   ├── agile/
        │   └── implementation/
        ├── project_management/
        ├── generation/
        ├── validation/
        ├── apply/
        └── verification/
```

This folder model preserves the distinction between project-level contracts, module-level contracts, planning artifacts, publishing artifacts, generated artifacts, validation outputs, applied changes, and verification results.

---

## 12. Pipeline 01: Context Engineering

### Purpose

Pipeline 01 creates a curated Context Package from manually authored project documents.

It answers:

```text
What do we know, and what context is safe and relevant for downstream AI-assisted work?
```

Pipeline 01 is the only pipeline that consumes manually authored requirement and architecture documents directly.

### Inputs

Pipeline 01 consumes only explicitly configured source documents.

For the CAutomation reference project, required source documents include:

```text
Project Client Contract
Project Engineering Contract
Pipeline Management SRS
Pipeline Management ATS
User & Client Management SRS
User & Client Management ATS
```

Optional supporting documents may be consumed only if explicitly enabled by configuration.

### Responsibilities

Pipeline 01 must:

- load project, pipeline, and task configuration,
- validate required input document profiles,
- normalize source documents,
- extract contract content,
- preserve project/module hierarchy,
- build the Context Package,
- validate the Context Package,
- preserve source provenance,
- write execution reports.

Raw source documents must not leak into later pipelines. Later pipelines must consume normalized/context artifacts.

### Module-Agnostic Validation Principle

Pipeline 01 must prove that CAutomation is project-aware and module-agnostic: one configured project, multiple configured modules, same reusable task implementations, no code changes per module.

### Task Sequence

Pipeline 01 should be implemented as:

```text
01 Load Context Configuration
02 Normalize Input Documents
03 Extract Contracts
04 Build Context Package
05 Validate Context Package
06 Write Context Execution Report
```

### Outputs

Pipeline 01 produces:

```text
normalized_input/
context/current/
context_package.json
context_package.md
context_manifest.json
context_sources.json
context_validation_report.json
context_summary.md
```

### Non-Responsibilities

Pipeline 01 must not generate Agile artifacts, implementation plans, project-management tickets, database metadata, source code, repository changes, or final application artifacts.

---

## 13. Pipeline 02: Planning

### Purpose

Pipeline 02 transforms the approved Context Package into the complete planning package required for project-management publishing and technical generation.

It answers:

```text
What work must be delivered, and what technical plan is required for Generation?
```

Planning is responsible for architectural decomposition. Generation is responsible for deterministic implementation.

### Inputs

Pipeline 02 consumes only approved Pipeline 01 outputs:

```text
context_package.json
context_manifest.json
context_validation_report.json
context_summary.md
normalized_input/
source traceability
```

It must not read raw project documents directly.

### Responsibilities

Pipeline 02 must:

- verify that Pipeline 01 completed successfully,
- read the Context Package,
- extract planning scope,
- generate the Agile Planning Package,
- generate the Technical Implementation Planning Package,
- define dependencies,
- define generation order,
- define traceability,
- validate planning completeness.

### Outputs: Agile Planning Package

Pipeline 02 must generate:

```text
epics.json / epics.md
features.json / features.md
user_stories.json / user_stories.md
tasks.json / tasks.md
acceptance_criteria.json / acceptance_criteria.md
dependencies.json
priorities.json
agile_traceability_matrix.json
agile_planning_report.json
```

These artifacts are tool-agnostic. They are not Jira tickets, Azure DevOps work items, or GitHub Project items.

### Outputs: Technical Implementation Planning Package

Pipeline 02 must generate:

```text
implementation_plan.json / implementation_plan.md
story_implementation_map.json
database_metadata.json
database_schema_plan.json
entity_model_plan.json
api_plan.json
backend_plan.json
frontend_plan.json
validation_plan.json
test_plan.json
dependency_graph.json
generation_order.json
artifact_manifest.json
technical_traceability_matrix.json
planning_validation_report.json
planning_summary.md
```

### Task Sequence

Pipeline 02 should be implemented as:

```text
01 Load Planning Configuration
02 Validate Planning Inputs
03 Extract Planning Scope
04 Generate Agile Planning Package
05 Generate Technical Implementation Planning Package
06 Validate Planning Package
07 Write Planning Execution Report
```

### Non-Responsibilities

Pipeline 02 must not generate source code, publish work items, modify repositories, apply artifacts, or execute final validation.

### Success Criteria

Pipeline 02 succeeds only when both planning packages are complete, internally consistent, deterministic, traceable to the Context Package, and ready for downstream consumption.

---

## 14. Pipeline 03: Project Management Publishing

### Purpose

Pipeline 03 publishes or synchronizes the Agile Planning Package into a configured project-management system.

It answers:

```text
How do we represent the approved Agile Planning Package in the selected project-management target?
```

Pipeline 03 does not create Agile artifacts. Pipeline 02 creates them. Pipeline 03 publishes them.

### Inputs

Pipeline 03 consumes only approved Pipeline 02 outputs:

```text
Agile Planning Package
planning_validation_report.json
planning_execution_report.json
agile_traceability_matrix.json
project_management_publishing_configuration
```

### Responsibilities

Pipeline 03 must:

- validate that the Planning pipeline completed successfully,
- load project-management publishing configuration,
- resolve the configured publisher adapter,
- publish or export the Agile Planning Package,
- capture external identifiers,
- update traceability,
- produce publishing reports,
- enforce the approval gate before Generation.

### Publisher Interface

Pipeline 03 uses a tool-agnostic publisher interface.

Supported publisher implementations may include:

```text
Jira Publisher
Azure DevOps Publisher
GitHub Projects Publisher
Linear Publisher
Markdown Publisher
JSON Publisher
```

The pipeline must not hard-code Jira-specific behavior into the core publishing workflow.

### Task Sequence

Pipeline 03 should be implemented as:

```text
01 Load Publishing Configuration
02 Validate Planning Inputs
03 Resolve Publishing Adapter
04 Publish Agile Planning Package
05 Build Publishing Traceability
06 Validate Publishing
07 Write Publishing Execution Report
```

### Outputs

Pipeline 03 produces:

```text
publication_report.json
publication_summary.md
publication_manifest.json
external_identifier_map.json
updated_agile_traceability_matrix.json
publishing_validation_report.json
approval_state.json
```

### Non-Responsibilities

Pipeline 03 must not generate implementation plans, source code, database metadata, backend code, frontend code, tests, repository changes, or final validation outputs.

---


### Planning Freeze / Generation Baseline Contract

Pipeline 03 must create a deterministic boundary between external project-management publishing and AI-driven implementation.

After the Agile Planning Package has been published or exported, Pipeline 03 must produce a frozen Generation Baseline before Pipeline 04 may execute.

The Generation Baseline must include:

```text
generation_baseline_manifest.json
frozen_agile_planning_package/
frozen_technical_implementation_planning_package/
frozen_external_identifier_map.json
baseline_checksum_manifest.json
approval_state.json
baseline_freeze_report.json
```

The baseline is immutable for the lifetime of a Generation run.

Pipeline 04 must consume the frozen baseline from Pipeline 03. Pipeline 04 must not read mutable backlog state directly from Jira, Azure DevOps, GitHub Projects, Linear, Markdown work queues, or any other external project-management target.

If a human modifies, reorders, deletes, or adds user stories in the external project-management tool after Pipeline 03 has created the baseline, that change does not automatically alter the Generation input. Instead, the baseline becomes stale and the workflow must be re-synchronized by re-running the appropriate Planning and Publishing steps.

Pipeline 03 must therefore support baseline state verification:

- verify that the external identifier map matches the frozen planning package;
- verify that approved user-story identifiers, acceptance criteria, and generation order match the baseline;
- detect external backlog drift where the configured publisher supports read-back validation;
- fail closed if drift is detected and no explicit re-baseline approval exists;
- record baseline hash values and approval timestamps in the publishing execution report.

This contract prevents Pipeline 04 from implementing unapproved backlog changes and preserves the separation between project-management synchronization and deterministic generation.

### Publisher Adapter Contract

Pipeline 03 remains tool-agnostic. Every publisher adapter must implement the same conceptual contract:

```text
load_configuration()
validate_target()
publish_agile_artifacts()
read_back_published_artifacts() where supported
build_external_identifier_map()
write_publication_report()
write_generation_baseline()
```

Adapter-specific behavior must remain inside the adapter. The core Pipeline 03 workflow must not contain Jira-specific, Azure-specific, GitHub-specific, Linear-specific, Markdown-specific, or JSON-export-specific branching beyond adapter resolution.
## 15. Pipeline 04: Generation

### Purpose

Pipeline 04 generates implementation artifacts into a controlled staging area.

It answers:

```text
How do we implement the approved user stories according to the technical plan?
```

Pipeline 04 is story-driven and test-first.

### Inputs

Pipeline 04 consumes approved outputs from Pipeline 02 and Pipeline 03:

```text
Agile Planning Package
Technical Implementation Planning Package
generation_order.json
artifact_manifest.json
approval_state.json
publication_report.json
external_identifier_map.json
```

### Story-Oriented Generation Rule

Pipeline 04 must implement the application epic by epic, feature by feature, and user story by user story, according to dependency order.

The Agile Planning Package defines the work units.

The Technical Implementation Planning Package defines how each work unit is implemented.

Pipeline 04 must not implement the application as one monolithic generation operation.

### Test-First Generation Rule

For each approved user story, Pipeline 04 must:

1. read the user story,
2. read its acceptance criteria,
3. read its technical implementation mapping,
4. generate tests first,
5. generate implementation artifacts,
6. run or verify story-level tests where practical,
7. write story-level traceability,
8. write a story-level generation report.

If a user story lacks acceptance criteria or technical implementation mapping, Pipeline 04 must stop for that story and emit a planning gap report.

### Generated Artifact Types

Pipeline 04 may generate staged artifacts for:

- PostgreSQL schema,
- migrations,
- seed data,
- FastAPI routers,
- Pydantic DTOs,
- application services,
- repositories,
- validators,
- authorization integration points,
- audit/reporting logic,
- React TypeScript screens,
- frontend API clients,
- UI components,
- tests,
- configuration,
- deployment-support artifacts,
- implementation documentation.

### Task Sequence

Pipeline 04 should be implemented as:

```text
01 Load Generation Configuration
02 Validate Generation Inputs
03 Build Story Generation Context
04 Generate Story Tests
05 Generate Story Implementation Artifacts
06 Verify Story-Level Generation
07 Build Generated Artifact Manifest
08 Write Generation Execution Report
```

Depending on implementation maturity, story implementation may internally decompose into database, backend, frontend, and test generation components, but the external generation unit remains the approved user story.

### Outputs

Pipeline 04 produces:

```text
generation/current/staging/
generated_artifact_manifest.json
generation_report.json
generation_summary.md
generation_traceability_matrix.json
story_generation_reports/
story_test_artifacts/
story_artifact_manifests/
planning_gap_reports/
```

### Non-Responsibilities

Pipeline 04 must not apply files to the live repository, bypass validation, invent requirements, modify project-management tools, change approved planning scope, or silently resolve specification gaps.

---

## 16. Pipeline 05: Validation

### Purpose

Pipeline 05 validates generated artifacts before they are applied.

It answers:

```text
Are the generated artifacts correct, complete, traceable, safe, and ready to be applied?
```

### Inputs

Pipeline 05 consumes approved Pipeline 04 outputs:

```text
Generated artifacts in staging
Generated artifact manifest
Story generation reports
Generation traceability matrix
Generated test artifacts
Generation execution report
```

### Responsibilities

Pipeline 05 must validate:

- generated files exist where the manifest says they exist,
- every generated artifact maps to a user story, task, acceptance criterion, and requirement,
- generated artifacts stay inside approved repository boundaries,
- database artifacts match schema contracts,
- backend artifacts match API/service/repository/validation contracts,
- frontend artifacts match approved screens and workflows,
- tests exist for every generated user story,
- tests pass where practical,
- project-level architecture and technology rules are respected,
- no unauthorized files are present.

### Validation Does Not Modify Artifacts

Pipeline 05 must never modify generated artifacts. It inspects, validates, reports, and stops on failure.

If correction is required, the workflow returns to Generation or Planning according to the defect type.

### Story-Oriented Validation

Pipeline 05 validates story by story.

For every user story, it must verify:

- implementation exists,
- acceptance criteria are covered,
- generated tests pass,
- traceability is complete,
- implementation conforms to SRS and ATS,
- project-level engineering contracts are respected.

### Task Sequence

Pipeline 05 should be implemented as:

```text
01 Load Validation Configuration
02 Validate Validation Inputs
03 Validate Artifact Manifest
04 Validate Traceability
05 Validate Architecture and Boundaries
06 Validate Database Artifacts
07 Validate Backend Artifacts
08 Validate Frontend Artifacts
09 Validate Test Artifacts
10 Execute Generated Tests
11 Build Validation Issue Report
12 Write Validation Execution Report
```

### Outputs

Pipeline 05 produces:

```text
validation_report.json
validation_summary.md
validation_issue_report.json
traceability_validation_report.json
architecture_validation_report.json
test_execution_report.json
apply_readiness_report.json
story_validation_reports/
```

---

## 17. Pipeline 06: Apply

### Purpose

Pipeline 06 applies validated implementation artifacts to the target repository.

It answers:

```text
How do we safely move validated artifacts from staging into the project repository?
```

Pipeline 06 does not generate, validate, or fix implementation artifacts.

### Inputs

Pipeline 06 consumes approved Pipeline 05 outputs:

```text
apply_readiness_report.json
validation_report.json
validation_summary.md
generated_artifact_manifest.json
validated generated artifacts
traceability_manifest.json
story_validation_results
apply_configuration
```

### Responsibilities

Pipeline 06 must:

- load apply configuration,
- perform apply preflight validation,
- verify Pipeline 05 completed successfully,
- verify apply authorization,
- apply validated artifacts,
- preserve repository integrity,
- record every applied artifact,
- produce apply reports.

### Transactional Apply

Pipeline 06 should behave transactionally where configured.

If an unrecoverable apply failure occurs during an atomic apply mode, the pipeline must restore the repository to its pre-apply state and produce a rollback report.

### Story-Oriented Apply

Pipeline 06 should apply artifacts story by story, preserving the traceability chain from user story to applied file.

### Task Sequence

Pipeline 06 should be implemented as:

```text
01 Load Apply Configuration
02 Validate Apply Inputs
03 Verify Apply Authorization
04 Resolve Repository Targets
05 Apply Story Artifacts
06 Verify Repository State
07 Update Repository Manifest
08 Write Apply Execution Report
```

### Outputs

Pipeline 06 produces:

```text
apply_execution_report.json
apply_summary.md
applied_artifact_manifest.json
repository_update_report.json
story_apply_reports/
updated_traceability_manifest.json
rollback_report.json
```

### Non-Responsibilities

Pipeline 06 must not regenerate artifacts, modify generated code, perform architectural validation, fix validation failures, execute implementation planning, or modify Agile artifacts.

---

## 18. Pipeline 07: Verification

### Purpose

Pipeline 07 performs final end-to-end verification of the repository after validated artifacts have been applied.

It answers:

```text
Did the AI Engine successfully deliver the application that was requested?
```

Pipeline 05 validates generated artifacts. Pipeline 06 applies them. Pipeline 07 verifies the final outcome.

### Inputs

Pipeline 07 consumes approved Pipeline 06 outputs:

```text
apply_execution_report.json
apply_summary.md
applied_artifact_manifest.json
repository_update_report.json
updated_traceability_manifest.json
repository_state
project_configuration
```

### Responsibilities

Pipeline 07 must:

- verify repository integrity,
- verify expected artifacts exist,
- verify no unexpected artifacts exist,
- verify traceability from requirements to implementation,
- verify project structure,
- verify pipeline reports,
- verify test reports,
- verify application completeness,
- produce final certification reports.

### Verification Scope

Pipeline 07 verifies:

- repository folder structure,
- artifact completeness,
- traceability completeness,
- test results,
- architecture compliance,
- module boundaries,
- repository boundaries,
- story completion,
- final project consistency.

### Traceability Chain

Pipeline 07 verifies that every generated artifact is traceable through:

```text
Requirement
↓
Acceptance Criteria
↓
User Story
↓
Feature
↓
Epic
↓
Planning Package
↓
Generated Artifact
↓
Applied Repository File
↓
Verification Result
```

### Task Sequence

Pipeline 07 should be implemented as:

```text
01 Load Verification Configuration
02 Validate Verification Inputs
03 Verify Repository Structure
04 Verify Artifact Completeness
05 Verify Traceability
06 Verify Architecture Compliance
07 Verify Test Results
08 Verify Story Completion
09 Build Final Certification Report
10 Write Verification Execution Report
```

### Outputs

Pipeline 07 produces:

```text
verification_execution_report.json
verification_summary.md
repository_verification_report.json
traceability_verification_report.json
application_completeness_report.json
final_ai_engine_certification_report.json
```

### Non-Responsibilities

Pipeline 07 must not regenerate artifacts, modify the repository, fix validation failures, apply new changes, or perform planning.

---

## 19. Artifact Flow and Traceability

The desired traceability chain is:

```text
WHAT/HOW document section
        ↓
normalized input artifact
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
technical implementation plan item
        ↓
generated test
        ↓
generated implementation artifact
        ↓
validation result
        ↓
applied file
        ↓
verification result
```

Every downstream artifact must be traceable to upstream artifacts. This allows humans and tools to audit why a file was generated and which approved requirement it supports.

---

## 19A. Shared Execution and Report Metadata Contract

All AI Engine reports must expose a common metadata envelope so that pipeline reports, task reports, validation reports, publishing reports, apply reports, administrative reports, and certification reports can be rendered consistently by the shared frontend shell.

The common report metadata envelope must include:

```text
report_id
report_type
project_id
module_id where applicable
pipeline_id where applicable
task_id where applicable
execution_id
story_id where applicable
source_requirement_ids
source_validation_ids
source_artifact_paths
produced_artifact_paths
started_at
finished_at
status
severity
summary
details_path or details_json
traceability_links
errors
warnings
```

Module-specific reports may extend this envelope with domain-specific fields. They must not remove or rename the common metadata fields.

The report envelope is a frontend and traceability contract. It does not require all reports to store identical business payloads, but it does require all reports to expose enough common metadata for unified filtering, navigation, audit review, and source-to-output traceability.

Validation and isolation-breach reports must preserve their domain-specific validation details while also satisfying this shared metadata envelope.

---

## 20. Artifact Lifecycle

Generated artifacts move through a clear lifecycle before they become authoritative inputs for downstream pipelines.

```text
Draft
    ↓
Generated
    ↓
Validated
    ↓
Reviewed
    ↓
Approved
    ↓
Authoritative
    ↓
Consumed by downstream pipeline
```

An artifact is not authoritative simply because it was generated. It becomes authoritative only after the required validation and approval steps for that artifact type have been completed.

---

## 21. Human Role and Approval Responsibilities

The human role is part of the architecture.

Humans are responsible for:

- manually authoring or approving initial project/module contracts,
- manually configuring projects, pipelines, tasks, and task configuration references through the web GUI where required,
- reviewing and approving generated Agile/project-management artifacts,
- approving generated implementation plans where configured,
- approving validated generated artifacts before Apply where configured,
- final acceptance.

Humans do not manually generate downstream artifacts. The AI Engine generates context, planning packages, publishing artifacts, implementation artifacts, validation reports, applied changes, and verification reports.

---

## 22. Approval Gates

Recommended approval gates are:

```text
After Pipeline 01: approve Context Package if required
After Pipeline 02: approve Planning Packages if required
After Pipeline 03: approve project-management publication before Generation
After Pipeline 05: approve validated generated artifacts before Apply
After Pipeline 07: accept or reject completed implementation
```

The most important approval gate before implementation is after Pipeline 03, because the published project-management backlog and planning outputs define the approved work that Generation is allowed to execute.

---

## 23. Pipeline Runtime Model

The AI Engine uses reusable runtime infrastructure under:

```text
CAutomation/ai_engine/runtime/
```

The runtime supports:

- configuration-driven pipeline execution,
- task registry resolution,
- task instance execution,
- task reporting,
- pipeline reporting,
- execution history,
- current-run management,
- shared path helpers,
- deterministic artifact paths.

Pipelines are orchestrators only. They execute reusable task definitions through configured task instances.

---


## 23A. Background Execution Resilience and Startup Reconciliation

The CAutomation runtime may use native FastAPI `BackgroundTasks` for process-local asynchronous execution where the approved engineering contract allows it. This decision does not imply that in-memory task state is authoritative.

All long-running executions must be persisted before asynchronous processing begins.

The persisted execution state must include:

```text
execution_id
project_id
module_id where applicable
pipeline_id or operation_type
started_by_user_id
active_client_id where applicable
status
requested_at
started_at
last_heartbeat_at where applicable
finished_at
input_artifact_refs
output_artifact_refs
error_summary
recovery_action
recovery_report_path
```

Native `BackgroundTasks` are best-effort process-local workers. They must not be treated as durable queues. A hard process crash, deployment restart, OOM event, or host termination may stop execution without running application-level exception handlers.

Therefore, application startup must run deterministic reconciliation for persisted executions left in transient states such as `Pending`, `Running`, `Applying`, or `RollingBack`.

Startup reconciliation must:

- scan persisted executions in transient states;
- compare timestamps, heartbeat data where available, and configured timeout rules;
- classify each stale execution as `Failed`, `Aborted`, or `Restartable` according to the owning operation contract;
- write a recovery report for every reconciled execution;
- update execution status before accepting dependent downstream work;
- prevent duplicate application of non-idempotent operations;
- require explicit configuration before any automatic restart is attempted.

The default recovery behavior is fail closed. If an execution cannot be proven safe to restart, it must be marked `Failed` or `Aborted` and require a new explicit execution request.

This resilience model preserves the project decision not to introduce external brokers such as Celery or Redis while preventing permanently stuck `Running` or `Pending` records from becoming invisible operational hazards.
## 24. Pipeline Folder Model

Pipeline definitions live under:

```text
CAutomation/ai_engine/pipelines/
```

Conceptual lifecycle folders:

```text
00_shared/
01_context_engineering/
02_planning/
03_project_management_publishing/
04_generation/
05_validation/
06_apply/
07_verification/
```

`00_shared` contains shared AI Engine resources. It does not replace the runtime.

Each pipeline may also own a pipeline-level shared folder for components reused by multiple tasks inside that pipeline.

---

## 25. Critical Boundary: Planning vs Generation

This boundary is non-negotiable.

Planning produces:

```text
Agile Planning Package
Technical Implementation Planning Package
dependency graph
generation order
artifact manifest
validation plan
test plan
```

Generation produces:

```text
story tests
story implementation artifacts
generated artifact manifest
generation reports
```

Planning decides what must be built and how it should be built.

Generation implements the approved work.

Generation must not invent architecture, requirements, stories, or scope.

---

## 25A. Platform Authority, Tenant Filter Bypass, and Frontend State Contract

### 25A.1 Default Tenant Isolation Rule

Repository-level tenant filtering remains mandatory by default.

For tenant-scoped data, repositories must apply the active client context supplied by the authenticated server-side request context. A tenant-scoped repository must not trust client-supplied `client_id` values without server-side validation.

### 25A.2 Controlled Platform-Authority Bypass

Some platform-level operations require cross-tenant visibility, such as platform-owner administration, system compliance review, or global user lookup.

Such operations may bypass the default repository-level `WHERE client_id = :active_client_id` injection only when all of the following are true:

- the authenticated user has an explicit platform-level authority such as `Platform Owner` or `System Administrator`;
- the operation is declared as platform-scoped in the service contract;
- the service calls an explicit repository method intended for platform scope rather than silently disabling filters;
- the request purpose and caller identity are written to an audit or administrative report;
- the response model is intentionally designed for platform-level visibility;
- tenant-scoped mutation remains forbidden unless the target tenant is explicitly selected and validated.

Bypass must be explicit in code and visible in review. Hidden flags, optional `client_id = None` behavior, or silent repository filter suppression are prohibited.

### 25A.3 Frontend Session and Context State Contract

The React TypeScript frontend must use a shared application context model for:

```text
authenticated session
current user
active client context
active project context
navigation state
permission state
```

The frontend must not invent independent tenant or project state per screen.

The active client and active project context must be resolved through approved backend APIs and stored in a shared frontend context provider. Navigation, forms, API clients, and screen-level components must consume this shared context.

### 25A.4 Token Propagation Contract

Frontend API calls must attach authenticated session context consistently through a single API client abstraction.

Screen components must not manually construct authorization headers or duplicate token handling logic. Token attachment, expiration handling, unauthorized response handling, and context refresh behavior belong in the shared API client/session layer.

The storage mechanism for tokens must be defined in the Project Engineering Contract. If the contract does not define it, Generation must not invent one. The Planning pipeline must produce the missing frontend/session implementation plan before Generation begins.

### 25A.5 Frontend Validation Contract

Frontend forms must mirror backend validation contracts and error response models.

Frontend validation may improve user feedback, but backend validation remains authoritative. Generated frontend forms must handle backend `ValidationErrorResponse` payloads deterministically and must not invent undocumented error shapes.

If a form validation library or state-management library is selected, it must be selected by Planning or by the Project Engineering Contract, not ad hoc by Generation.

---

## 26. Expected Review Questions for External AI Models

This document should be given to other AI models for review and audit.

Suggested review questions:

1. Is the seven-pipeline sequence logically sound?
2. Are the boundaries between Context Engineering, Planning, Project Management Publishing, Generation, Validation, Apply, and Verification clear?
3. Does Pipeline 02 produce enough planning detail for Pipeline 04?
4. Does Pipeline 03 keep project-management publishing tool-agnostic?
5. Does Pipeline 04 support story-driven, test-first implementation?
6. Are the proposed artifacts sufficient for traceability?
7. Is the separation between project artifacts and pipeline runtime artifacts clear?
8. Are the approval gates in the right places?
9. Does the workflow support deterministic AI-assisted software engineering?
10. Does the task architecture support isolated execution and testing?
11. Does the CAutomation reference project provide enough information to validate the workflow?

---

## 27. Current Implementation Position

At the time this document is drafted, Pipeline 01 exists as the most mature reference implementation. The current implementation already uses a simplified pipeline structure close to:

```text
01_context_engineering
02_planning
03_generation
04_validation
05_apply
06_verification
```

This specification defines the target synchronized workflow:

```text
01_context_engineering
02_planning
03_project_management_publishing
04_generation
05_validation
06_apply
07_verification
```

The implementation should be audited against this specification and updated where required.

---

## 28. Success Criteria

The AI Engine workflow is successful when it can use the approved project-level and module-level contracts for the CAutomation reference project to produce a validated, deliverable web application while preserving traceability and human control throughout the process.

Success means that the workflow demonstrates:

- manually authored WHAT/HOW documents are transformed into a curated Context Package,
- Planning produces both Agile and Technical Implementation Planning Packages,
- Project Management Publishing synchronizes Agile artifacts through a configured adapter,
- humans approve the published/planned work before Generation,
- Generation implements approved user stories using a test-first workflow,
- generated artifacts are created in staging rather than applied directly,
- Validation happens before Apply,
- Apply is controlled, transactional where configured, and traceable,
- Verification confirms the applied result,
- every important generated artifact can be traced back to its upstream source.

---

## 28A. Freeze Criteria and Change Governance

This workflow specification may be frozen as the authoritative AI Engine architectural contract when the following are true:

1. the seven-pipeline architecture is reflected consistently in the workflow specification, project engineering contract, implementation folder model, and pipeline entry points;
2. every pipeline has a documented input contract, output contract, preflight contract, execution report contract, and downstream approval or readiness contract;
3. the Pipeline 03 Planning Freeze / Generation Baseline contract is implemented in the specification and represented in planned artifacts;
4. background execution recovery and startup reconciliation are specified for long-running operations;
5. platform-authority bypass rules are explicit, audited, and prohibited by default for normal tenant-scoped operations;
6. frontend state, token propagation, navigation context, and validation contracts are specified sufficiently for deterministic React TypeScript generation;
7. shared execution/report metadata is defined for unified frontend rendering and traceability;
8. shared-component promotion rules are defined and accepted;
9. lifecycle status enumerations are either domain-specific or explicitly declared as shared;
10. future deviations are managed as controlled change requests rather than implementation drift.

After freeze, implementation synchronization must proceed pipeline by pipeline against this specification. The implementation must conform to the frozen contract; the contract must not be silently adjusted to match incidental implementation shortcuts.

---

## 29. Summary

CAutomation should not jump directly from contracts to code generation.

The intended workflow is staged:

```text
Manual WHAT/HOW documents
        ↓
Context Package
        ↓
Planning Packages
        ↓
Project Management Publishing
        ↓
Human Approval
        ↓
Story-Driven Test-First Generation
        ↓
Validation
        ↓
Apply
        ↓
Verification
```

This separation is the foundation of the CAutomation AI Engine.

It preserves provenance, maintains human control, validates AI output, supports project-management synchronization, and builds software through a repeatable pipeline-based workflow rather than unstructured prompting.

Version 2 completes the final architectural hardening iteration before implementation synchronization. The AI Engine now has an explicit planning freeze boundary, controlled publishing-to-generation transition, deterministic recovery model for process-local background execution, a platform-authority bypass contract, a shared frontend state and token propagation contract, common reporting metadata, shared-component promotion governance, and freeze criteria.

The next engineering phase is implementation synchronization: inspect the current AI Engine implementation pipeline by pipeline, compare it to this frozen workflow contract, and bring the code, configuration, tests, reports, and documentation into conformance.
