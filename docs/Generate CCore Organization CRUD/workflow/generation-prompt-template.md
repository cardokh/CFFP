# Generation Prompt Template

## Purpose

This document defines how the Automation Factory should assemble the AI prompt for the `Generate CRUD Module -> Organization` task.

The final prompt must be assembled from controlled documents and runtime inspection output. It must not be written as a loose one-off prompt.

## Prompt Assembly Inputs

The final prompt must include these sections in this order:

1. Task objective.
2. No-guessing rule.
3. Technology decisions.
4. CCore vertical slice blueprint.
5. Generation contract.
6. Artifact mapping specification summary.
7. Organization CRUD specification.
8. AI artifact manifest contract.
9. Validation rules.
10. Repository inspection summary.
11. Golden reference summary and selected file contents.
12. Required output format.

## Prompt Template

```text
You are generating artifacts for the CFFP Automation Factory task:

Generate CRUD Module -> Organization

You must follow all control documents and runtime inspection results provided below.

NON-NEGOTIABLE RULES
- Do not guess.
- Do not invent missing architecture.
- Do not introduce new frameworks or dependencies.
- Do not output patches or snippets.
- Do not modify files outside the allowed artifact mapping.
- If required information is missing, return no code artifacts and list requiredManualDecisions.

TECHNOLOGY DECISIONS
{{technology_decisions}}

CCORE VERTICAL SLICE BLUEPRINT
{{ccore_vertical_slice_blueprint}}

GENERATION CONTRACT
{{generation_contract}}

ARTIFACT MAPPING
{{artifact_mapping_summary}}

ENTITY SPECIFICATION
{{ccore_organizations_spec}}

AI ARTIFACT MANIFEST CONTRACT
{{ai_artifact_manifest_contract}}

VALIDATION RULES
{{crud_generation_validation_rules}}

REPOSITORY INSPECTION SUMMARY
{{repository_inspection_summary}}

GOLDEN REFERENCE SUMMARY
{{golden_reference_summary}}

GOLDEN REFERENCE FILE CONTENTS
{{golden_reference_file_contents}}

REQUIRED OUTPUT
Return only a valid JSON artifact manifest matching the AI Artifact Manifest Contract.
Do not wrap the JSON in markdown.
Do not include commentary before or after the JSON.
```

## Missing Information Behavior

If any required decision is missing, the AI must return a manifest with:

```json
{
  "manifestVersion": "1.0",
  "generationRequest": {},
  "technologyStack": {},
  "artifacts": [],
  "requiredManualDecisions": [
    {
      "field": "",
      "question": "",
      "reason": ""
    }
  ],
  "validationHints": [],
  "generationNotes": []
}
```

## Forbidden Prompt Behavior

The prompt builder must not:

- omit validation rules,
- omit artifact mapping,
- omit technology decisions,
- provide only a high-level summary when exact specs are available,
- include unrelated historical documents by default,
- ask the AI to directly edit the repository.
