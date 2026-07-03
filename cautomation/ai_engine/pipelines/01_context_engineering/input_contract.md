# Input Contract

The Context Engineering pipeline consumes human-authored and approved project knowledge.

## Required Project Input Root

```text
projects/<project>/input/
├── client/
├── engineering/
└── modules/
```

## Human-Authored Input

The human team is responsible for supplying enough project knowledge for the platform to understand what should be generated.

The platform may report missing, weak, ambiguous, or conflicting input, but it must not silently invent missing business intent.

## Expected Input Categories

### client/

Client-facing documents explain what the product is and why it exists.

Examples:

- vision
- problem statement
- goals
- success criteria
- user groups
- personas
- workflows

### engineering/

Engineering documents define technical boundaries.

Examples:

- architecture principles
- technology constraints
- security constraints
- coding standards
- data constraints
- integration constraints
- definition of done

### modules/

Module documents define functional areas.

Examples:

- module overview
- domain model
- user stories
- acceptance criteria
- workflow descriptions
- permission requirements

## Forbidden Inputs

The pipeline must not depend on:

- conversation history
- unapproved assumptions
- arbitrary source code inspection
- unrelated repository files
- model memory

## Missing Input Handling

Missing input must be reported explicitly.

The pipeline may continue only when the missing input is non-blocking and the report clearly states the limitation.
