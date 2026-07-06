# CAutomation AI Engine Workflow Specification

Version: Draft 4  
Status: Review Draft  
Scope: CAutomation AI Engine workflow, pipeline responsibilities, artifact flow, reference-project contract, and approval gates  
Reference Project: Pipeline Management  
Last Updated: July 2026

---

## 1. Executive Summary

**CAutomation is a generic AI-assisted software engineering framework.**

Its purpose is to transform a small set of manually authored project specifications into a complete, deliverable web application through a sequence of deterministic automation pipelines. The framework does not treat AI as a one-shot code generator. Instead, it uses AI as part of a structured engineering workflow where every stage has explicit inputs, explicit outputs, validation, traceability, and human approval gates.

The current reference project is **Pipeline Management**. Pipeline Management is used to validate the AI Engine workflow because it is both a realistic software project and the future web-based operational interface for CAutomation itself. Through Pipeline Management, users should eventually be able to create projects, define pipelines, configure tasks, execute pipelines, inspect outputs, review validation results, and approve generated artifacts.

The intended end-to-end flow is:

```text
Reference Project: Pipeline Management
│
├── WHAT document
├── HOW document
└── selected supporting documents
        ↓
01 Context Engineering
        ↓
Context Package
        ↓
02 Agile Artifact Generation
        ↓
Epics, Features, User Stories, Tasks, Acceptance Criteria
        ↓
Human Review and Approval
        ↓
03 Implementation Planning
        ↓
Technical implementation plan and generation contract
        ↓
04 Generation
        ↓
Generated implementation artifacts in staging
        ↓
05 Validation
        ↓
Validated generated artifacts
        ↓
Human Approval to Apply
        ↓
06 Apply
        ↓
Applied repository/project changes
        ↓
07 Verification
        ↓
Verified deliverable web application
```

The most important early rule is:

> After Context Engineering, the next pipeline generates Agile artifacts only. It does not generate code or implementation plans.

This document should be treated as the architectural workflow contract for future pipeline implementation.

---

## 2. Purpose of This Document

This document describes the intended workflow for the **CAutomation AI Engine**.

The goal is to define what the AI Engine is trying to achieve, how the workflow should be structured, what each pipeline should consume, what each pipeline should generate, where generated artifacts should live, and where human approval is required.

This document is intended to be reviewed by humans and by other AI models before the remaining pipelines are implemented. It should act as a shared architectural reference so future implementation work does not drift from the agreed workflow.

This is not a Python implementation guide. It is a workflow, artifact, and pipeline-contract specification.

---

## 3. Background and Inspiration

The CAutomation AI Engine is inspired by the article **Professional Grade AI-Assisted Coding: Context Is Everything with BMAD and Spec Kit** by Bill Catlan, published in CODE Magazine.

The article argues that professional-grade AI-assisted coding depends on more than sending prompts to an AI model. It emphasizes deliberate context engineering, provenance preservation, structured artifacts, focused context sessions, and staged software engineering work.

CAutomation adopts those principles, but it does **not** attempt to implement BMAD, Spec Kit, or any other existing methodology directly. CAutomation defines its own workflow, artifact model, approval gates, and execution pipelines.

The core idea is:

> CAutomation should not simply ask an AI model to generate code. It should automate a structured software engineering process.

The AI Engine should transform manually authored project specifications into increasingly concrete engineering artifacts through deterministic pipelines. Each pipeline has explicit inputs, explicit outputs, validation, traceability, and human approval gates where appropriate.

---

## 4. Vision

The long-term vision is to create software that can be given a small set of manually authored project documents and then use AI-assisted software engineering to progressively produce the artifacts required to deliver an end-to-end web application.

The intended final result is not only source code. The complete result should include, where applicable:

- Agile artifacts,
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

The AI Engine should be reusable across projects. The current reference project is **Pipeline Management**, which is used to validate the framework and demonstrate the complete workflow.

---

## 5. Reference Project: Pipeline Management

CAutomation should be described as a generic AI-assisted software engineering framework.

The framework itself should not be tied to any specific business application. To validate the framework, the current reference project is:

```text
Pipeline Management
```

Pipeline Management is used as the first project that the AI Engine will process end-to-end. It provides realistic requirements and technical constraints without making the AI Engine itself project-specific.

Pipeline Management is not merely a sample application. It is intended to become the web-based operational interface for CAutomation. The module should eventually allow users to create and manage AI-assisted software engineering projects, define pipelines, configure reusable task definitions, configure pipeline task instances, execute pipelines, inspect execution history, review generated artifacts, inspect validation results, and approve or reject artifacts before downstream pipelines continue.

In that sense, Pipeline Management has two roles:

1. **Reference project** — it is the first realistic project used to validate that the AI Engine can transform manually authored project specifications into a complete deliverable web application.
2. **Operational control plane** — it is the future user interface through which humans operate, supervise, and govern CAutomation workflows.

CAutomation is the automation engine. Pipeline Management is the cockpit used to configure, visualize, execute, and control that engine.

As the operational web interface, Pipeline Management should make the automation workflow visible and manageable. A user should not need to understand or manually run the underlying Python pipelines in order to operate the system. Instead, the web interface should expose the major concepts of the AI Engine in user-facing form: projects, input documents, context packages, pipelines, task definitions, task instances, executions, generated artifacts, validation results, approval gates, and execution history.

This means the Pipeline Management module is both the first project generated through the AI Engine and the interface that later allows humans to manage the AI Engine itself. It should provide the visibility, control, review, approval, and audit capabilities required for human-supervised AI-assisted software engineering.

For the reference project, the human provides two manually authored documents:

```text
WHAT document
HOW document
```

These two documents are the authoritative inputs for the reference project.

### 5.1 WHAT Document

The WHAT document describes what the software should do.

It should focus on product intent and business functionality. Typical content includes:

- product or module purpose,
- business goals,
- user goals,
- functional requirements,
- major workflows,
- important use cases,
- scope,
- out-of-scope items,
- business rules,
- success criteria.

The WHAT document should not primarily describe implementation technology. Its purpose is to define the product and functional intent.

### 5.2 HOW Document

The HOW document describes how the software should be implemented.

It should focus on technical direction, architecture, implementation constraints, technology choices, standards, and engineering expectations. Typical content includes:

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

The HOW document does not replace the WHAT document. It constrains and guides the implementation of the functionality described in the WHAT document.

### 5.3 Supporting Documents

Future projects may include additional manually authored documents, such as:

- ADRs,
- UX notes,
- UI sketches,
- style guides,
- domain notes,
- validation rules,
- external constraints,
- existing-system summaries.

Supporting documents must be explicitly selected. The AI Engine should not read arbitrary files unless a pipeline contract allows it.

---

## 6. End-to-End Workflow

The high-level workflow is:

```text
Human-authored WHAT/HOW documents
        ↓
01 Context Engineering
        ↓
Context Package
        ↓
02 Agile Artifact Generation
        ↓
Epics, Features, User Stories, Tasks, Acceptance Criteria
        ↓
Human Review and Approval
        ↓
03 Implementation Planning
        ↓
Technical implementation plan and generation contract
        ↓
04 Generation
        ↓
Generated implementation artifacts in staging
        ↓
05 Validation
        ↓
Validated generated artifacts
        ↓
Human Approval to Apply
        ↓
06 Apply
        ↓
Applied repository/project changes
        ↓
07 Verification
        ↓
Post-apply verification result
```

The most important early boundary is this:

> After Context Engineering, the next pipeline generates Agile artifacts only. It does not generate code, database metadata, backend plans, frontend plans, or implementation plans.

The Agile artifacts define the work. Only after those artifacts are reviewed and approved should the AI Engine move into implementation-oriented pipelines.

---

## 7. Core Design Principles

### 6.1 Automate Software Engineering, Not Prompting

CAutomation should automate a staged engineering workflow. It should not behave like an unconstrained coding assistant.

### 6.2 Project Artifacts Are the Source of Truth

Conversation history must not be authoritative. Pipelines should consume declared artifacts and produce declared artifacts.

### 6.3 Context Engineering Comes First

The AI model should not generate planning or implementation artifacts from vague context. The first stage must create a curated context package from the human-authored project inputs.

### 6.4 Agile Artifacts Before Implementation

The workflow treats software engineering as an Agile process. After context engineering, the AI Engine should first produce Agile planning artifacts. These must be reviewed and approved before implementation planning or code generation begins.

### 6.5 Provenance Must Be Preserved

Every important generated artifact should be traceable back to its inputs.

### 6.6 Pipelines Have One Clear Responsibility

Each pipeline must do one kind of work. A pipeline should not perform work that belongs to a later stage.

### 6.7 Human Approval Gates Are Part of the Workflow

Generated outputs are not automatically trusted. Important artifacts must be reviewed and approved before downstream pipelines consume them.

### 6.8 AI Output Is Untrusted Until Validated

AI-generated artifacts must be validated, inspected, and approved before they become authoritative inputs for later stages.

---

## 8. Pipeline Contract Overview

| Pipeline | Purpose | Primary Inputs | Primary Outputs | Approval Gate |
|---|---|---|---|---|
| 01 Context Engineering | Build trusted AI context from human-authored project inputs | WHAT, HOW, selected supporting documents | Context Package, context manifest, source traceability | Optional context approval |
| 02 Agile Artifact Generation | Produce the Agile backlog from the Context Package | Context Package | Epics, Features, User Stories, Technical Stories, Tasks, Acceptance Criteria, dependencies, priorities | Required Agile approval |
| 03 Implementation Planning | Convert approved Agile work into technical implementation plans | Approved Agile artifacts, Context Package | Implementation plan, artifact manifest, dependency graph, generation order, database/API/backend/frontend/test plans | Optional/Recommended implementation-plan approval |
| 04 Generation | Generate implementation artifacts into staging | Approved implementation plan, Context Package, approved Agile artifacts | Generated files, generated artifact manifest, generation report | No direct trust; must go to validation |
| 05 Validation | Validate generated artifacts before apply | Generated artifacts, manifests, approved plans, validation rules | Validation report, issue report, traceability validation | Required approval before apply |
| 06 Apply | Apply validated artifacts to the target project/repository | Validated artifacts, apply config, approval | Applied files, apply report, change summary | Approval required before or during apply depending on mode |
| 07 Verification | Verify the project after apply | Applied state, apply report, tests, acceptance criteria | Verification report, regression/test report | Final acceptance |

---

## 9. Project Artifact Location Model

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
CAutomation/projects/pipeline_management/
```

Pipeline folders contain reusable pipeline definitions, tasks, configuration, and runtime logic. They are not the primary location for durable project artifacts.

Durable project artifacts should be written under the relevant project folder.

---

## 10. Reference Project Folder Sketch

A conceptual project folder for the Pipeline Management reference project is:

```text
CAutomation/
└── projects/
    └── pipeline_management/
        ├── project.json
        ├── input/
        │   ├── WHAT.md
        │   ├── HOW.md
        │   └── supporting/
        │
        ├── context/
        │   ├── current/
        │   ├── approved/
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

This is a target model. The implementation may introduce these folders incrementally.

---

## 11. Pipeline 01: Context Engineering

### Purpose

Pipeline 01 creates a curated context package from manually authored project documents.

It answers:

```text
What do we know, and what context is safe and relevant for downstream AI-assisted work?
```

### Inputs

For the Pipeline Management reference project, Pipeline 01 consumes only the manually authored project and module contract documents declared by the pipeline configuration. Source documents may be authored in supported external formats, with PDF as the primary contract format and DOCX/Markdown retained as secondary development/reference formats where configured.

```text
CAutomation/projects/pipeline_management/input/client/<configured project client contract>
CAutomation/projects/pipeline_management/input/engineering/<configured project engineering contract>
CAutomation/projects/pipeline_management/input/modules/pipeline_management/<configured WHAT/SRS source document>
CAutomation/projects/pipeline_management/input/modules/pipeline_management/<configured HOW/ATS source document>
```

Task 02 input contracts are defined as explicit document profiles. Required profiles are blocking inputs. Optional profiles are extension points that must be declared, disabled by default, and ignored unless explicitly enabled by configuration. Future project profiles may enable supporting-document inputs such as UI Specification, Database Specification, API Contract, UX Specification, or Security Specification, but Pipeline 01 must consume only explicitly configured project/module input artifacts. Raw source documents are never the canonical input for downstream tasks. Task 02 must normalize supported source formats into `normalized_input/`, and later tasks must consume that normalized workspace.

### Outputs

```text
CAutomation/projects/pipeline_management/context/current/
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

### Task Sequence

Pipeline 01 is implemented as six ordered tasks:

1. **Load Configuration**
2. **Normalize Input Documents**
3. **Extract Contracts**
4. **Build Context Package**
5. **Validate Context Package**
6. **Write Execution Report**

#### Task 01 - Load Configuration

Task 01 loads and validates the configured Pipeline 01 execution contract before any input validation, extraction, or context-package work begins.

Task 01 must:

- load the pipeline-level configuration,
- load the reusable task-definition registry,
- verify required pipeline configuration groups,
- verify required pipeline identity values,
- verify that reusable task definitions exist,
- verify that pipeline task instances exist,
- verify that every task instance references a known task definition,
- write a machine-readable task state file,
- write a task execution report,
- return a failed task status when the configuration contract is invalid.

Task 01 does not read, validate, or normalize the content of the manually authored project specification documents. That responsibility belongs to Task 02.

### Responsibilities

Pipeline 01 should validate required inputs, extract relevant content, preserve source provenance, separate functional intent from technical constraints, build the context package, validate it, and write execution reports.

Pipeline 01 is the perimeter defense for context quality. It must not allow raw human-authored files to leak into later tasks. Raw documents can be PDF, DOCX, Markdown, or another explicitly supported format, but downstream tasks must consume one canonical internal format.

Task 02, Normalize Input Documents, is the hard minimum viable input quality gate. It validates the required source documents, verifies that their formats are supported, proves that their content can be extracted, rejects unreadable/empty/template-nonconformant inputs, and writes a canonical normalized input workspace before any downstream task continues. If Task 02 passes, the pipeline has the minimum trusted normalized input required to continue. If Task 02 fails, the pipeline must stop before any context package can be created.

Task 02 must use a source-format normalizer abstraction. The task orchestration layer detects each source document format, delegates extraction to the matching normalizer implementation, and writes the canonical Markdown plus metadata outputs. Format-specific parsing rules belong inside dedicated normalizers, such as PDF, DOCX, and Markdown normalizers. Downstream tasks must remain isolated from source-format parsing details.

The canonical normalized workspace is written under the project folder, next to the raw `input/` folder. For the current CAutomation reference project, Task 02 normalizes both project-level and module-level contracts into the same canonical workspace:

```text
CAutomation/projects/<project_id>/normalized_input/modules/<module_id>/
├── project_client_contract.md
├── project_engineering_contract.md
├── module_srs.md
├── module_ats.md
├── normalization_manifest.json
└── normalization_report.json
```

After Task 02 succeeds, later Pipeline 01 tasks must consume `normalized_input/` and must not read raw `input/` source documents directly. This rule isolates source-format complexity in one task and gives PDF, DOCX, Markdown, and future supported formats a single downstream representation. PDF is the primary source-document format for the current CAutomation development path and reference tests. DOCX and Markdown remain supported by existing normalizers, but they are not the main engineering focus of this phase.

Task 02 treats the following source PDFs as required minimum input contracts for the Pipeline Management reference project:

- `input/client/Project_Client_Contract.pdf` - required project-level client contract.
- `input/engineering/Project_Engineering_Contract.pdf` - required project-level engineering contract.
- `input/modules/<module_id>/Software_Requirements_Specification.pdf` - required module-level WHAT/SRS contract.
- `input/modules/<module_id>/Architecture_and_Technical_Specification.pdf` - required module-level HOW/ATS contract.

Task 02 also defines disabled optional document-profile extension points for future UI, database, API, UX, and security specifications. These optional profiles do not participate in the quality gate until enabled by the active project configuration.

Task 02 validation responsibilities are implementation-agnostic and profile-driven. It checks structural completeness, source-format eligibility, readability/extractability, non-empty normalized content, required section coverage, placeholder indicators, and basic cross-document readiness required by the active document profiles. The architectural contract must not hard-code module-specific artifacts; instead, the active configuration defines which specification artifacts, sections, identifiers, and relationships are mandatory for the current project/module type.

Task 03, Extract Contracts, owns the deeper extraction-phase checks identified by the external review against the normalized Markdown inputs. After Task 02 has created the canonical normalized workspace, Task 03 must validate and extract contract content for richer semantic quality. This includes Markdown linting, acronym and reference validation, cross-reference validation, conflicting technical-parameter detection, and rejection of undefined acronyms before any context_package.json artifact is compiled.

Task 05, Validate Context Package, remains separate from Task 02 and Task 03. Task 02 validates and normalizes source specifications. Task 03 validates and extracts normalized contracts. Task 05 validates the assembled context package after extraction and compilation. This separation preserves single responsibility and makes it possible to distinguish human input defects, normalization defects, extraction defects, and context-package compilation defects.

Validation failures must not cause unhandled runtime crashes. When Task 02 rejects the inputs, downstream extraction and compilation tasks must not run, but Pipeline 01 must still execute the reporting path and produce a structured, machine-readable execution report that explains the validation gaps and the final failed status.

Repository-state comparison is intentionally out of scope for Pipeline 01. Pipeline 01 maps approved intent into trusted context; comparison between new intent and an existing generated or deployed codebase belongs to a later validation, synchronization, or apply-stage concern.

### Non-Responsibilities

Pipeline 01 must not create Agile artifacts, implementation plans, database metadata, frontend/backend plans, or code.

---

## 12. Pipeline 02: Agile Artifact Generation

### Purpose

Pipeline 02 generates Agile planning artifacts from the context package.

It answers:

```text
What work needs to be done from a product and delivery perspective?
```

This pipeline is about Agile planning, not technical implementation planning.

### Inputs

```text
CAutomation/projects/pipeline_management/context/current/
```

### Outputs

```text
CAutomation/projects/pipeline_management/agile/current/
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

### Responsibilities

Pipeline 02 should generate epics, features, user stories, technical stories where appropriate, tasks, acceptance criteria, dependencies, priorities, and traceability back to the context package.

### Non-Responsibilities

Pipeline 02 must not generate database metadata, API specifications, backend implementation plans, frontend implementation plans, source code, repository changes, or final implementation decisions.

### Human Approval Gate

Pipeline 02 must be followed by human review and approval.

Approved Agile artifacts should be promoted to:

```text
CAutomation/projects/pipeline_management/agile/approved/
```

Downstream implementation pipelines should consume approved Agile artifacts, not draft Agile artifacts.

---

## 13. Pipeline 03: Implementation Planning

### Purpose

Pipeline 03 converts approved Agile artifacts into technical implementation plans.

It answers:

```text
How should each approved story be implemented?
```

This is the first stage where database metadata, API plans, backend plans, frontend plans, test plans, and generation manifests may be produced.

### Inputs

```text
CAutomation/projects/pipeline_management/agile/approved/
CAutomation/projects/pipeline_management/context/current/
```

### Outputs

```text
CAutomation/projects/pipeline_management/implementation/current/
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
database_metadata.json
database_schema_plan.json
entity_model_plan.json
api_plan.json
backend_plan.json
frontend_plan.json
test_plan.json
deployment_plan.json
```

### Responsibilities

Pipeline 03 should map approved stories to implementation units, identify database/API/backend/frontend/test changes, define dependencies, define generation order, and produce a machine-readable implementation contract for the Generation pipeline.

### Non-Responsibilities

Pipeline 03 must not generate final source code, apply repository changes, or bypass the approved Agile backlog.

---

## 14. Pipeline 04: Generation

### Purpose

Pipeline 04 generates implementation artifacts from the approved implementation plan.

### Inputs

```text
CAutomation/projects/pipeline_management/implementation/approved/
CAutomation/projects/pipeline_management/context/current/
CAutomation/projects/pipeline_management/agile/approved/
```

### Outputs

```text
CAutomation/projects/pipeline_management/generation/current/
```

Expected artifacts may include:

```text
generated_artifact_manifest.json
generation_report.json
generation_traceability_matrix.json
staging/
```

Generation targets may include:

```text
database/
backend/
frontend/
testing/
deployment/
```

### Non-Responsibilities

Pipeline 04 must not invent unapproved stories, rewrite Agile scope, apply files directly to the live repository, or mark generated output as trusted without validation.

---

## 15. Pipeline 05: Validation

### Purpose

Pipeline 05 validates generated artifacts before they are applied.

### Inputs

- generated artifacts,
- generated artifact manifest,
- implementation plan,
- approved Agile artifacts,
- context package,
- validation rules.

### Outputs

```text
CAutomation/projects/pipeline_management/validation/current/
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

### Responsibilities

Pipeline 05 should validate completeness, manifest consistency, traceability, HOW-document constraints, architecture, coding standards where practical, tests where practical, and apply safety.

### Non-Responsibilities

Pipeline 05 must not apply changes to the live repository or silently fix generated artifacts without recording provenance.

---

## 16. Pipeline 06: Apply

### Purpose

Pipeline 06 applies validated generated artifacts to the target repository or target project location.

### Inputs

- validated generated artifacts,
- validation report,
- generated artifact manifest,
- apply configuration,
- human approval if required.

### Outputs

```text
CAutomation/projects/pipeline_management/apply/current/
```

Expected artifacts may include:

```text
apply_report.json
applied_artifact_manifest.json
backup_manifest.json
change_summary.md
```

### Responsibilities

Pipeline 06 should apply only validated artifacts, respect allowed target paths, preserve backups or change records, record exactly what changed, and produce an apply report.

### Non-Responsibilities

Pipeline 06 must not generate new implementation artifacts, bypass validation, or apply files outside approved scope.

---

## 17. Pipeline 07: Verification

### Purpose

Pipeline 07 verifies the repository after changes have been applied.

### Inputs

- applied repository state,
- apply report,
- validation rules,
- test configuration,
- approved Agile artifacts and implementation plan for traceability.

### Outputs

```text
CAutomation/projects/pipeline_management/verification/current/
```

Expected artifacts may include:

```text
verification_report.json
verification_summary.md
post_apply_test_report.json
regression_report.json
```

### Responsibilities

Pipeline 07 should run post-apply checks, verify expected files exist, run tests where practical, verify story-level acceptance criteria where practical, report failures clearly, and preserve traceability.

---

## 18. Artifact Flow and Traceability

The desired traceability chain is:

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

Every downstream artifact should be traceable to upstream artifacts. This allows humans and tools to audit why a file was generated and which approved requirement it supports.

---

## 19. Artifact Lifecycle

Generated artifacts should move through a clear lifecycle before they become authoritative inputs for downstream pipelines.

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

For example, Agile artifacts generated by Pipeline 02 should remain draft artifacts until they have been reviewed and approved by a human. Only then should they be promoted into the approved Agile artifact location and consumed by Implementation Planning.

This lifecycle is important because it prevents downstream pipelines from consuming unreviewed or untrusted AI output.

---

## 20. Human Role and Approval Responsibilities

The human role is part of the architecture, not an external afterthought. CAutomation should automate repeatable engineering work, but humans remain responsible for direction, judgement, approval, and final acceptance.

For each major stage, the workflow should make clear:

- what the AI Engine produces,
- what the human reviews,
- what the human approves or rejects,
- what artifact becomes authoritative after approval,
- which downstream pipeline is allowed to consume the approved artifact.

The most important approval gate in the early workflow is the approval of Agile artifacts. Once approved, the Agile backlog defines the work that later implementation and generation pipelines are allowed to execute.

---

## 21. Approval Gates

Recommended approval gates are:

```text
After Pipeline 01: approve context package if needed
After Pipeline 02: approve Agile artifacts
After Pipeline 03: approve implementation plan if needed
After Pipeline 05: approve validated generated artifacts before apply
After Pipeline 07: accept or reject completed implementation
```

The most important early gate is after Pipeline 02, because generated Agile artifacts define the work that later implementation pipelines will execute.

---

## 22. Pipeline Runtime Model

The AI Engine uses reusable runtime infrastructure under:

```text
CAutomation/ai_engine/runtime/
```

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

### 22.1 Standard Task and Pipeline Execution Layers

All pipeline and task implementations must expose a standard execution surface before higher-level AI Engine or CAutomation runners are introduced. This standard is part of the architectural contract and applies to every current and future pipeline.

#### Task-level execution standard

Every task folder must contain:

```text
run_task.py
run_task_tests.py
```

`run_task.py` is the only standard entry point for executing one task directly. It must:

- execute exactly one task implementation,
- preserve the configured task instance identity when the task is launched by a pipeline,
- produce a standard task execution result,
- produce a machine-readable task execution report,
- expose status, return code, elapsed time, stdout, stderr, task identity, pipeline identity, execution id, and report paths,
- return a non-zero process exit code when the task execution status is failed.

`run_task_tests.py` is the only standard entry point for executing one task test suite. It must:

- execute the task unit tests,
- execute the task functional tests,
- execute the task validation tests,
- aggregate the three test categories,
- produce a standard task test report,
- expose status, return code, elapsed time, stdout, stderr, test category, and report paths,
- return a non-zero process exit code when any required task test category fails.

Each task test suite must be organized into the following categories:

```text
unit/
functional/
validation/
```

The test report structure must remain stable enough to be consumed later by the planned CAutomation web GUI.

#### Pipeline-level execution standard

Every pipeline folder must contain:

```text
run_pipeline.py
run_pipeline_tests.py
```

`run_pipeline.py` is the only standard entry point for executing one pipeline directly. It must:

- execute every configured task in sequence,
- call each task through its `run_task.py` entry point,
- respect configured task order and blocking dependencies,
- aggregate task execution results,
- produce a standard pipeline execution report,
- expose status, execution id, elapsed time, task results, stdout, stderr, and report paths,
- return a non-zero process exit code when the pipeline execution status is failed.

`run_pipeline_tests.py` is the only standard entry point for executing one pipeline test suite. It must:

- execute every configured task through that task's `run_task_tests.py` entry point,
- aggregate task test reports,
- produce a standard pipeline test report,
- expose status, elapsed time, task test results, stdout, stderr, and report paths,
- return a non-zero process exit code when any required task test runner fails.

#### Future execution levels

The following higher-level execution entry points are planned but are not part of the current implementation scope:

```text
run_ai_engine.py
run_ai_engine_tests.py
run_cautomation.py
run_cautomation_tests.py
```

They must later consume the task and pipeline reports defined above instead of introducing a conflicting report model.

---

## 23. Pipeline Folder Model

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

The exact numbering and folder names may be adjusted incrementally, but responsibility boundaries should remain explicit.

### 23.1 runtime vs 00_shared

```text
runtime    = shared engine execution code
00_shared  = shared pipeline resources, templates, schemas, examples, or reusable configuration patterns
```

`00_shared` should not replace the engine runtime.

---

## 24. Critical Boundary: Agile Planning vs Implementation Planning

This boundary is non-negotiable.

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

## 25. Expected Review Questions for External AI Models

This document should be given to other AI models for review and audit, together with the Pipeline Management WHAT and HOW documents.

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
10. Does the Pipeline Management reference project provide enough information to validate the workflow?
11. What risks or inconsistencies should be addressed before implementing Pipeline 02?

---

## 26. Current Implementation Position

At the time this document is drafted, Pipeline 01 is the reference implementation for the framework.

The framework already supports these architectural ideas:

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

The next implementation step should not begin until this workflow specification has been reviewed and the responsibility of Pipeline 02 is confirmed:

```text
Pipeline 02 = Agile Artifact Generation only
```

---

## 27. Success Criteria

The AI Engine workflow should be considered successful when it can use the approved WHAT and HOW documents for the Pipeline Management reference project to produce a validated, deliverable web application while preserving traceability and human control throughout the process.

Success means that the workflow can demonstrate all of the following:

- the WHAT and HOW documents are transformed into a curated Context Package,
- Agile artifacts are generated before implementation work begins,
- Agile artifacts are reviewed and approved before implementation planning,
- implementation plans are derived from approved Agile artifacts,
- generated artifacts are created in staging rather than applied directly,
- validation happens before apply,
- apply is controlled and traceable,
- verification confirms the applied result,
- every important generated artifact can be traced back to its upstream source.

The goal is not only to generate code. The goal is to demonstrate a repeatable AI-assisted software engineering workflow that can produce a complete, reviewed, validated, and deliverable web application.

---

## 28. Summary

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

It allows the system to preserve provenance, maintain human control, validate AI output, and build software through a repeatable pipeline-based workflow rather than through unstructured prompting.
