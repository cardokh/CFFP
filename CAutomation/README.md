# CAutomation

CAutomation is the reusable automation workspace for the AI-assisted software development platform.

The long-term purpose is to support a repeatable flow where one or more human-authored project documents are transformed into a complete, validated, deliverable web application.

```text
Human-authored Project Input
        ↓
Context Engineering
        ↓
Planning
        ↓
Generation
        ├── Database
        ├── Backend
        ├── Frontend
        ├── Testing
        └── Deployment
        ↓
Validation
        ↓
Apply
        ↓
Verification
```

Pipeline Management is the reference project used to design, test, and evolve this platform. The automation must remain generic enough to support future projects.

## Top-Level Areas

- `ai_engine/` contains reusable platform pipelines.
- `projects/` contains project-specific input and configuration.

## Human Responsibility

The human team provides project knowledge under `projects/<project>/input/`.

This includes client documents, engineering constraints, module definitions, workflows, acceptance criteria, architecture decisions, and other approved project knowledge.

The human team does not manually assemble prompts for downstream generators.

## Platform Responsibility

The platform turns the human-authored input into validated, traceable context packages and then uses those packages to plan, generate, validate, apply, and verify software artifacts.

The first automated stage is `01_context_engineering`. It replaces the earlier idea of a narrow requirements pipeline.
