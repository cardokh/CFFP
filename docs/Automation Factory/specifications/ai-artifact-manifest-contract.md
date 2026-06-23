# AI Artifact Manifest Contract

## Purpose

The `Generate CRUD Module` task must not accept free-form AI output as implementation code.

The AI must return a structured artifact manifest. The Automation Factory stages, validates, and applies the artifacts from that manifest.

## Output Format

The AI output must be valid JSON.

The root object must use this structure:

```json
{
  "manifestVersion": "1.0",
  "generationRequest": {
    "taskName": "Generate CRUD Module",
    "targetEntity": "",
    "sourceSpecification": "",
    "goldenReference": []
  },
  "technologyStack": {
    "database": "",
    "backend": "",
    "frontend": "",
    "orchestration": "",
    "aiProvider": "",
    "aiModel": ""
  },
  "artifacts": [
    {
      "artifactType": "",
      "targetPath": "",
      "changeType": "create|replace",
      "contentEncoding": "utf-8",
      "content": "",
      "reason": "",
      "sourceReference": ""
    }
  ],
  "requiredManualDecisions": [],
  "validationHints": [],
  "generationNotes": []
}
```

## Manifest Rules

- `artifacts` must contain full file contents.
- Patch fragments are not allowed.
- Markdown code fences are not allowed inside `content`.
- `targetPath` must be repository-relative.
- Absolute paths are forbidden.
- Generated paths must match the concrete entity specification.
- Every generated file must map to one declared output in the specification.
- The AI must not create undeclared files unless it places the file in `requiredManualDecisions` and stops.
- If a needed decision is missing, the AI must return no code artifacts and must populate `requiredManualDecisions`.

## Allowed Artifact Types

- `database_schema_config`
- `database_seed_config`
- `backend_domain_object`
- `backend_constants`
- `backend_messages`
- `backend_contracts`
- `backend_mapper`
- `backend_validator`
- `backend_repository_protocol`
- `backend_repository_implementation`
- `backend_service`
- `backend_routes`
- `backend_init`
- `backend_api_paths_update`
- `backend_route_registry_update`
- `backend_service_factory_update`
- `backend_service_container_update`
- `frontend_list_html`
- `frontend_details_html`
- `frontend_list_js`
- `frontend_details_js`
- `frontend_css`
- `frontend_navigation_update`
- `test_file`
- `validation_report`

## Forbidden AI Output

The AI must not output:

- advice instead of artifacts
- partial snippets
- diff patches
- shell commands as a replacement for artifacts
- guessed architecture
- guessed database choices
- guessed frontend framework choices
- guessed route paths
- guessed file locations

## Staging Rule

The pipeline writes AI artifacts to the staging directory first.

The pipeline then validates staged files.

Only after validation succeeds may the pipeline apply files to the repository.
