# External AI Review Prompt

You are asked to perform a critical review and audit of two documents that will be provided with this prompt:

1. `AI-Assisted-Coding.pdf`
2. `CAutomation_AI_Engine_Workflow_Specification.md`

## Context

We are designing an AI-assisted software engineering automation system called **CAutomation**.

The goal of CAutomation is to take a small set of manually authored project documents and use AI-assisted, pipeline-driven automation to progressively produce a complete, end-to-end, deliverable web application.

The intended workflow is inspired by the ideas in the AI-assisted coding/context engineering paper, especially:

- context engineering;
- preserving provenance;
- structured artifact generation;
- deterministic stages instead of ad hoc prompting;
- human review and approval gates;
- using AI as an engineering assistant rather than an uncontrolled code generator.

However, CAutomation is **not intended to be a direct implementation of BMAD, Spec Kit, or any other specific methodology**. We are creating our own workflow and architecture, inspired by the principles discussed in the paper.

## What We Are Trying To Do

The system starts with manually created specification documents. At minimum, these include:

- a **WHAT** document describing what the software should do, including business intent, functionality, users, workflows, and expected outcomes;
- a **HOW** document describing how the software should be implemented, including architecture, technology choices, coding standards, constraints, database approach, backend approach, frontend approach, validation approach, and other implementation guidance.

These documents are then processed by a sequence of automation pipelines.

The first pipeline performs **Context Engineering**. Its purpose is to read the manually authored documents, validate them, extract useful information, preserve provenance, and create a structured context package for the following pipelines.

The next major stage should generate **Agile artifacts**. This is important because we view software engineering as an Agile process, not simply as code generation. Before implementation begins, the system should produce reviewable planning artifacts such as epics, features, user stories, technical stories, tasks, dependencies, and acceptance criteria.

Only after the Agile artifacts are reviewed and approved should later pipelines move toward implementation planning, code generation, validation, and applying generated artifacts to the target application.

## Your Task

Please review both documents carefully and be extremely critical.

Do not merely summarize the documents. We want a serious architectural and methodological audit.

Please evaluate:

1. Whether the proposed CAutomation workflow is clear and coherent.
2. Whether the workflow is properly inspired by the context engineering paper without blindly copying BMAD or Spec Kit.
3. Whether the distinction between context engineering, Agile artifact generation, implementation planning, code generation, validation, and apply stages is clear.
4. Whether the proposed pipeline boundaries make sense.
5. Whether Agile artifacts are placed at the correct stage in the workflow.
6. Whether the human approval gates are sufficient and correctly positioned.
7. Whether the workflow preserves provenance and traceability strongly enough.
8. Whether the document clearly explains what inputs each pipeline consumes and what outputs each pipeline produces.
9. Whether anything important is missing before the system could realistically generate a complete web application.
10. Whether any parts of the document are vague, contradictory, over-engineered, under-specified, or likely to cause implementation problems later.

## Specific Questions

Please answer these questions directly:

1. Is the overall concept sound?
2. Is the proposed pipeline sequence appropriate?
3. Should any pipeline be split, merged, renamed, or reordered?
4. Is Agile artifact generation correctly separated from implementation/code generation?
5. Are the initial WHAT and HOW documents sufficient as the primary manual inputs, or should additional manually authored documents be required?
6. What artifacts should absolutely exist before implementation/code generation begins?
7. What are the biggest risks in this architecture?
8. What would you change before implementation continues?
9. What would you keep exactly as it is?
10. What would you ask the project owner to clarify?

## Review Style

Please be direct, specific, and critical.

Use the following structure in your response:

1. Executive Summary
2. Strengths
3. Major Concerns
4. Missing or Weak Areas
5. Pipeline-by-Pipeline Review
6. Artifact and Traceability Review
7. Agile Methodology Review
8. Context Engineering Review
9. Recommendations
10. Final Verdict

Where possible, provide concrete examples of improved wording, improved pipeline boundaries, or improved artifact structures.

Please do not assume the architecture is correct. Challenge it.
