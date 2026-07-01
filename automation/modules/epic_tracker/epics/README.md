# Epics

This folder defines the ordered end-to-end software delivery lifecycle.

The current architecture uses eight high-level epics:

```text
01 Requirements & Constraints Analysis
        ↓
02 Solution Design
        ↓
03 Project Planning / Epic Tracker
        ↓
04 Database Generation
        ↓
05 Backend Generation
        ↓
06 Frontend Generation
        ↓
07 Testing
        ↓
08 Deployment
```

## Core principle

Every epic must produce a complete, validated output contract that is sufficient for the next epic to execute without asking additional questions.

This means each epic has:

- an input contract,
- an output contract,
- validation rules,
- reports,
- user stories,
- implementation tasks,
- test suites,
- test cases.

## Automation principle

Epic 1 is the main clarification gate. Human/client clarification is expected there.

After Epic 1, the pipeline should increasingly rely on structured metadata and validated contracts to automate the remaining epics.

If an epic cannot produce a complete output contract, the pipeline must stop rather than continue with hidden assumptions.
