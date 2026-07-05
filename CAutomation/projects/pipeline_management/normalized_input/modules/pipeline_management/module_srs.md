Software Requirements Specification

CAutomation / CCore / Pipeline Management

Document status: Generation-readiness draft contract for the Pipeline Management reference project. Only this SRS and the matching ATS are manually authored and approved at module level. This iteration hardens the module contract for deterministic planning and generation while preserving the contextual Pipeline plus reusable Task plus PipelineTask association model.

1. Purpose, Scope, and Source-of-Truth Rule

This SRS defines what the Pipeline Management epic must support from a business and product perspective. It is a functional contract, not an implementation design. It defines the approved hierarchy, functional concepts, workflows, rules, validation expectations, and acceptance criteria used by the CAutomation AI Engine.

The SRS answers what must be built and why it is required.

The ATS answers how the approved SRS is implemented.

The ATS must not introduce business requirements absent from this SRS.

If generated artifacts conflict with this SRS, this SRS wins.

If behavior must change, this SRS is updated and approved before regeneration.

2. Business Context and Approved Hierarchy

The Pipeline Management epic belongs to the following approved CAutomation hierarchy. The labels must appear consistently in generated agile artifacts, UI labels, reports, and traceability output.

| Level | Approved value | Business meaning |
| --- | --- | --- |
| Project | CAutomation | The top-level software initiative and product family boundary. |
| Product | CCore | The core CAutomation product that owns shared platform capabilities. |
| Module | CAutomation | The automation module that manages AI-driven generation workflows. |
| Epic | Pipeline Management | The functional epic for defining reusable tasks, creating contextual pipelines, executing pipeline runs, and reporting results. |

3. In Scope and Out of Scope

| In scope | Out of scope |
| --- | --- |
| Maintain Projects, Products, Modules, Pipelines, reusable Tasks, PipelineTask associations, Pipeline Executions, Pipeline Task Executions, and Reports. | Changing repository folder structure or creating new AI Engine pipeline folders. |
| Maintain metadata for Project Type, Project Status, Project Target, Product Type, Product Status, Product Target, Module Type, Module Status, and Module Target. | Defining a platform-wide authentication, authorization, or tenant model. |
| Create pipelines inside a selected Project/Product/Module context and add reusable tasks to those pipelines. | Executing arbitrary AI prompts outside approved pipeline definitions. |
| Generate agile planning artifacts from approved functional scope. | Inventing requirements during planning, generation, validation, apply, or verification. |
| Expose deterministic validation and reporting behavior. | Replacing project-level contracts; project-level SRS/ATS documents are deferred to a later iteration. |

4. Actors and Permissions

| Actor | Business responsibility | Required permissions |
| --- | --- | --- |
| Product Owner | Approves SRS scope, acceptance criteria, and business rule changes. | Read all, approve specification changes. |
| Automation Architect | Maintains hierarchy, metadata, reusable task catalog, pipeline definitions, task placement, and lifecycle. | Create, read, update, archive, restore, validate. |
| Developer | Consumes generated artifacts and reviews implementation output. | Read, validate, view reports. |
| Reviewer | Inspects generated plans, validation findings, execution reports, and traceability. | Read, view reports. |
| AI Engine | Consumes approved SRS and ATS to generate artifacts. | Read approved contracts only. |

5. Business Domain Model

The domain separates the contextual pipeline definition from the reusable task catalog. A Pipeline is created for a selected Project/Product/Module context. A Task is reusable and may appear in many Pipelines. PipelineTask is the association that places one reusable Task inside one Pipeline with order, requirement, configuration, retry policy, and failure behavior. This prevents the system from treating a task as owned by only one pipeline.

| Entity | Business description | Parent or association | Lifecycle expectation |
| --- | --- | --- | --- |
| Project | Top-level initiative such as CAutomation. | None | Draft, Active, Suspended, Archived. |
| Project Type/Status/Target | Metadata that classifies project purpose, lifecycle, and delivery target. | None | Active or Archived lookup value. |
| Product | Product owned by a project, such as CCore. | Project | Draft, Active, Suspended, Archived. |
| Product Type/Status/Target | Metadata that classifies product purpose, lifecycle, and delivery target. | None | Active or Archived lookup value. |
| Module | Module owned by a product, such as CAutomation. | Product | Draft, Active, Suspended, Archived. |
| Module Type/Status/Target | Metadata that classifies module purpose, lifecycle, and delivery target. | None | Active or Archived lookup value. |
| Pipeline | Named, versioned workflow definition created inside selected Project/Product/Module context. | Project + Product + Module context | Draft, Active, Deprecated, Archived. |
| Task | Reusable task definition that can be used in many pipelines. | Global reusable catalog | Draft, Active, Disabled, Archived. |
| PipelineTask | Association that places a Task into a Pipeline and stores sequence/order/configuration. | Pipeline plus Task | Active, Disabled, Archived. |
| Pipeline Execution | Run record created when a pipeline is executed. | Pipeline | Pending, Running, Passed, Failed, Cancelled. |
| Pipeline Task Execution | Run record created for one PipelineTask during a pipeline execution. | Pipeline Execution plus PipelineTask | Pending, Running, Passed, Failed, Skipped. |
| Report | Generated report associated with a pipeline execution or task execution. | Execution record | Generated, Reviewed, Archived. |

6. Functional Requirements

| ID | Requirement | Area |
| --- | --- | --- |
| SRS-FR-001 | The system shall maintain Project records with code, name, description, type, status, target, ownership, and audit information. | Project |
| SRS-FR-002 | The system shall maintain Product records under exactly one Project. | Product |
| SRS-FR-003 | The system shall maintain Module records under exactly one Product. | Module |
| SRS-FR-004 | The system shall maintain lookup metadata for type, status, and target for Projects, Products, and Modules. | Metadata |
| SRS-FR-005 | The system shall create Pipeline definitions after the user selects Project, Product, and Module context. | Pipeline |
| SRS-FR-006 | The system shall maintain a reusable Task catalog independent of any single Pipeline. | Task |
| SRS-FR-007 | The system shall allow one Task to be used by multiple Pipelines through PipelineTask association records. | PipelineTask |
| SRS-FR-008 | The system shall store PipelineTask ordering, required/optional behavior, configuration, retry policy, and failure behavior per Pipeline. | PipelineTask |
| SRS-FR-009 | The system shall prevent activation of a Pipeline unless required context, metadata, and at least one active PipelineTask exist. | Lifecycle |
| SRS-FR-010 | The system shall create Pipeline Execution records that snapshot the selected Pipeline version and ordered PipelineTask list. | Execution |
| SRS-FR-011 | The system shall create Pipeline Task Execution records for each executable PipelineTask in the execution snapshot. | Execution |
| SRS-FR-012 | The system shall expose execution status, task status, timestamps, messages, and report references. | Reporting |
| SRS-FR-013 | The system shall generate planning artifacts from SRS functional requirements, rules, workflows, and acceptance criteria. | Planning |
| SRS-FR-014 | The system shall never allow downstream AI stages to invent business scope not present in approved SRS. | AI Boundary |

7. Business Data and Field Rules

| Entity scope | Business field | Rule |
| --- | --- | --- |
| All primary entities | id | Required stable identifier. User-visible only where useful for traceability. |
| All primary entities | name | Required human-readable name. Must be unique within approved parent boundary where applicable. |
| All primary entities | code | Required stable short code for generation, traceability, and reporting. |
| All primary entities | description | Optional business description. |
| Project/Product/Module | type/status/target | Required references to active metadata values before activation. |
| Pipeline | project/product/module context | Required context selected before pipeline creation; product must belong to project and module must belong to product. |
| Pipeline | version | Required version value. Active pipelines are versioned. |
| Task | task_key | Required stable reusable task key, unique in task catalog. |
| PipelineTask | pipeline + task | Required association between one Pipeline and one reusable Task. |
| PipelineTask | sequence_order | Required positive integer unique within the pipeline. |
| PipelineTask | configuration/retry/failure behavior | Optional or required according to task type; stored per pipeline usage, not globally on the reusable task. |
| Execution records | status | Required lifecycle status. Must follow allowed transitions. |
| Report | report_type | Required classifier such as planning, validation, apply, verification, or execution summary. |

8. Relationship and Lifecycle Rules

A Product cannot exist without a Project.

A Module cannot exist without a Product.

A Pipeline is created only after selecting a valid Project, Product, and Module context.

A Pipeline context must be internally consistent: Product belongs to Project, and Module belongs to Product.

A Task is reusable and must not be owned by one Pipeline, Project, Product, or Module.

A PipelineTask must reference exactly one Pipeline and exactly one Task.

The same Task may be used by multiple Pipelines through multiple PipelineTask records.

A PipelineTask sequence order must be unique within its Pipeline.

A Pipeline Execution must reference the Pipeline version and ordered PipelineTask snapshot executed.

A Pipeline Task Execution must reference the Pipeline Execution and the PipelineTask snapshot or identity.

Archived parent records must not accept new active child records.

Deletion is not a normal business operation; archive is the expected lifecycle action.

9. User Workflows

| Workflow | Required behavior |
| --- | --- |
| Create hierarchy | User creates or selects Project, Product, and Module before defining pipelines. |
| Configure metadata | User selects valid type, status, and target metadata for Project, Product, and Module. |
| Define reusable task | User creates or selects a reusable Task with stable key, name, type, description, and default responsibility. |
| Define pipeline | User selects Project, Product, and Module context, then creates a named and versioned Pipeline. |
| Add tasks to pipeline | User adds reusable Tasks to a Pipeline through PipelineTask records with sequence order and usage-specific configuration. |
| Validate pipeline | User validates completeness before activation. Validation returns stable rule identifiers. |
| Execute pipeline | System creates execution records from the approved pipeline and ordered PipelineTask snapshot. |
| Review reports | User reviews generated reports linked to execution records and task execution records. |

10. Validation Rules

| Rule ID | Rule |
| --- | --- |
| SRS-VAL-001 | Required fields must be present before save when the field is mandatory for the current action. |
| SRS-VAL-002 | Names and codes must be unique within the approved parent boundary. |
| SRS-VAL-003 | A status transition must be one of the allowed lifecycle transitions. |
| SRS-VAL-004 | Activation requires required metadata references to be active. |
| SRS-VAL-005 | Pipeline activation requires selected Project/Product/Module context to be valid and active. |
| SRS-VAL-006 | Pipeline activation requires at least one active PipelineTask. |
| SRS-VAL-007 | PipelineTask sequence_order must be unique and positive within the Pipeline. |
| SRS-VAL-008 | A PipelineTask must reference an active reusable Task before activation. |
| SRS-VAL-009 | Execution records must not be edited as definitions after creation. |
| SRS-VAL-010 | Reports must reference an existing execution record. |

11. Acceptance Criteria

| ID | Acceptance criterion |
| --- | --- |
| SRS-AC-001 | Generated agile artifacts include Project, Product, Module, Pipeline, reusable Task, PipelineTask, Execution, and Reporting scope. |
| SRS-AC-002 | Generated schema includes metadata lookup tables for type, status, and target at Project, Product, and Module levels. |
| SRS-AC-003 | Generated schema represents Pipeline and Task as separate entities connected by PipelineTask many-to-many association records. |
| SRS-AC-004 | Generated APIs preserve selected Project/Product/Module pipeline context and do not expose child records outside their approved boundary. |
| SRS-AC-005 | Generated UI supports create, view, update, validate, archive, restore, task selection, pipeline task ordering, execution, and report review where applicable. |
| SRS-AC-006 | Generated tests assert validation rule identifiers, lifecycle transitions, many-to-many task reuse, and execution snapshot behavior. |
| SRS-AC-007 | Generated reports trace execution output back to approved pipeline, PipelineTask, and reusable Task definitions. |

12. Deterministic Generation Boundary

Planning may derive epics, features, user stories, tasks, and acceptance tests only from the approved SRS. Generation may consume both SRS and ATS. If required information is missing, the AI Engine must produce a specification gap and must not infer hidden business behavior. The current iteration does not add new AI Engine pipeline folders and does not create project-level contracts; those project-level documents are deferred.

13. Entity-Level Functional Contract

| Entity | Create | Read | Update | Special functional rule |
| --- | --- | --- | --- | --- |
| Project | Authorized architect may create. | List and detail views required. | Allowed while not archived. | Represents CAutomation or future top-level initiatives. |
| Product | Created under one Project. | List under Project and detail required. | Allowed while parent is usable. | Represents CCore in current epic. |
| Module | Created under one Product. | List under Product and detail required. | Allowed while parent is usable. | Represents CAutomation in current epic. |
| Pipeline | Created after selecting Project/Product/Module context. | List by context and detail required. | Allowed while draft or inactive. | Defines a versioned contextual workflow. |
| Task | Created in reusable task catalog. | List/search for selection into pipelines. | Allowed while not locked by immutable execution snapshots. | Reusable across multiple pipelines. |
| PipelineTask | Created by adding a Task to a Pipeline. | Shown in ordered sequence. | Allowed while pipeline is editable. | Represents usage/configuration of a reusable Task in one Pipeline. |
| Pipeline Execution | Created by execution action. | Detail and status view required. | Status updates only. | Represents one run of a pipeline version and task snapshot. |
| Pipeline Task Execution | Created from pipeline execution. | Shown under execution detail. | Status/message updates only. | Represents one PipelineTask run. |
| Report | Generated from planning, validation, execution, apply, or verification. | List and detail views required. | Review status may change. | Provides traceability and evidence. |

14. Lifecycle Transition Contract

| Record type | Allowed normal transitions | Blocked transitions |
| --- | --- | --- |
| Project/Product/Module | Draft to Active, Active to Suspended, Suspended to Active, Active/Suspended to Archived, Archived to Draft or Suspended when restored. | Archived directly to Active without validation; Active to Draft after child records exist. |
| Pipeline | Draft to Active, Active to Deprecated, Deprecated to Archived, Draft to Archived, Archived to Draft when restored. | Active without valid context, active metadata, and at least one active PipelineTask. |
| Task | Draft to Active, Active to Disabled, Disabled to Active, any non-running state to Archived. | Archived or disabled task selected for new active PipelineTask without reactivation. |
| PipelineTask | Active to Disabled, Disabled to Active, Active/Disabled to Archived. | Duplicate sequence order in the same Pipeline; missing reusable Task. |
| Pipeline Execution | Pending to Running, Running to Passed, Running to Failed, Pending/Running to Cancelled. | Passed or Failed back to Running; Cancelled to Passed. |
| Pipeline Task Execution | Pending to Running, Pending to Skipped, Running to Passed, Running to Failed. | Passed/Failed back to Pending; Skipped to Running after parent execution is complete. |
| Report | Generated to Reviewed, Generated/Reviewed to Archived. | Archived to Reviewed without restore action. |

15. Agile Artifact Generation Contract

| Generated artifact | SRS source material | Required deterministic output |
| --- | --- | --- |
| Epic | Business hierarchy and SRS purpose/scope. | One epic named Pipeline Management under CAutomation / CCore. |
| Features | Functional requirements and business domain model. | Feature groups for hierarchy management, metadata management, reusable task catalog, pipeline definition, execution, reporting, and validation. |
| User stories | Actors, workflows, functional requirements, and validation rules. | Stories with role, goal, reason, acceptance criteria, and traceability IDs. |
| Implementation tasks | SRS functional areas plus ATS technical mapping. | Tasks for schema, API, service, frontend, validation, tests, and reports. |
| Acceptance tests | SRS acceptance criteria and validation rules. | Positive and negative tests using stable rule identifiers. |
| Specification gaps | Missing required SRS or ATS details. | Explicit blocking gap records instead of invented behavior. |

16. Business Scenarios

| Scenario | Given | When | Then |
| --- | --- | --- | --- |
| Create CAutomation hierarchy | No current hierarchy exists for the epic. | An authorized architect creates CAutomation, CCore, and Pipeline Management with active metadata. | The hierarchy is available for pipeline definition and appears in generated planning artifacts. |
| Create reusable task | The task catalog is available. | The architect creates a task such as Validate Output or Generate Report. | The task can be selected into multiple pipelines without duplication. |
| Create contextual pipeline | A Project/Product/Module context exists and is active. | The architect selects CAutomation, CCore, and Pipeline Management and creates a pipeline. | The pipeline is saved as Draft in the selected context. |
| Add reusable tasks | A draft pipeline exists and reusable tasks exist. | The architect adds tasks to the pipeline with sequence order and configuration. | PipelineTask records define the ordered workflow without changing the reusable task definitions. |
| Validate invalid pipeline | A pipeline has missing active tasks or inactive metadata. | The user validates or attempts activation. | The system returns stable validation rule identifiers and blocks activation. |
| Execute active pipeline | A pipeline is active and contains active ordered PipelineTasks. | The user starts execution. | A pipeline execution and task execution records are created from the snapshot. |
| Review reports | An execution has completed or failed. | The user opens execution reports. | The report list shows generated summaries and links them to the execution and task statuses. |

End of SRS.

17. Generation Readiness Pass

This section defines the functional completeness checks that must pass before the AI Engine treats the module SRS and ATS as generation-ready. The checks do not add new business scope; they prevent generation from filling gaps with invented requirements.

| Readiness area | Required SRS decision | Generation behavior if missing |
| --- | --- | --- |
| Business hierarchy | Project CAutomation, Product CCore, and Module Pipeline Management must be present. | Block generation and report missing hierarchy contract. |
| Pipeline context | Pipeline must be created only after Project, Product, and Module are selected and validated. | Block pipeline generation and report missing context rule. |
| Task reuse | Task must be reusable globally; PipelineTask must associate one Task with one Pipeline. | Block schema and API generation if Pipeline and Task are collapsed into one table. |
| Lifecycle | Allowed statuses and transitions must be explicit for hierarchy records, pipelines, tasks, executions, and reports. | Generate lifecycle gap instead of inventing statuses. |
| Validation | Validation rule IDs must be stable and traceable. | Generate validation-gap report if rule identifiers are missing. |
| Acceptance evidence | Each generated story, test, API, or table must cite at least one SRS requirement or acceptance criterion. | Reject untraced output during validation. |

18. Approved Functional Status Values

The following status value sets are approved at business level. The ATS may implement them as lookup rows or constrained constants, but generated artifacts must preserve the exact semantic values.

| Record type | Approved statuses | Business note |
| --- | --- | --- |
| Project | Draft, Active, Suspended, Archived | Archived is not deleted and must remain reportable. |
| Product | Draft, Active, Suspended, Archived | Product status is evaluated before module and pipeline activation. |
| Module | Draft, Active, Suspended, Archived | Module must be Active before creating an Active pipeline. |
| Pipeline | Draft, Active, Deprecated, Archived | Deprecated pipelines are retained for traceability but not preferred for new executions. |
| Task | Draft, Active, Disabled, Archived | Disabled tasks cannot be selected into newly activated pipelines. |
| PipelineTask | Active, Disabled, Archived | Disabled associations are excluded from new execution snapshots. |
| PipelineExecution | Pending, Running, Passed, Failed, Cancelled | Passed, Failed, and Cancelled are terminal. |
| PipelineTaskExecution | Pending, Running, Passed, Failed, Skipped | Skipped applies when optional or dependency-blocked tasks are not run. |
| Report | Generated, Reviewed, Archived | Report records must remain linked to their execution source. |

19. Specification Gap Handling

A specification gap is a blocking finding that identifies missing information needed for deterministic generation. The AI Engine must report gaps rather than invent missing behavior, fields, endpoints, screens, tests, or repository paths.

| Gap type | Example | Required output |
| --- | --- | --- |
| Business gap | A required workflow is referenced but has no acceptance criterion. | Gap record with SRS section, missing decision, severity, and recommended clarification. |
| Data gap | An entity appears in the SRS but lacks required business field rules. | Gap record naming the entity and missing field rule. |
| Lifecycle gap | A status exists without allowed transition rules. | Gap record naming record type and missing transition. |
| Traceability gap | Generated artifact has no SRS requirement or acceptance criterion source. | Reject generated artifact and report traceability failure. |
| Implementation mapping gap | SRS requirement has no ATS implementation mapping. | Block generation until ATS maps the SRS requirement. |

20. Minimum Generation Scope

A generation run for this module is complete only when it can deterministically produce agile artifacts, database schema, backend APIs and services, frontend screens, validation rules, tests, and reports for the approved Pipeline Management scope. Project-level SRS and ATS contracts remain deferred and must not be generated in this iteration.
