# Frontend CRUD Automation

Generates the CCore Pipeline frontend module from the existing CCore Tasks frontend module.

The Tasks module is the golden template. The generator reuses its list-page HTML structure, table/search/sort/pagination JavaScript patterns, CSS class conventions, protected workspace loading, and dashboard layout.

## Generate

```bash
python automation/factory/crud/frontend/generate_frontend.py --repo-root .
```

Generated files:

- `frontend/static/desktop/protected/ccore/automation/pipelines/pipelines.html`
- `frontend/static/desktop/protected/ccore/automation/pipelines/css/pipelines.css`
- `frontend/static/desktop/protected/ccore/automation/pipelines/js/pipelines.js`
- `frontend/static/desktop/protected/ccore/automation/pipelines/pipeline-details.html`
- `frontend/static/desktop/protected/ccore/automation/pipelines/css/pipeline-details.css`
- `frontend/static/desktop/protected/ccore/automation/pipelines/js/pipeline-details.js`
- `frontend/static/shared/api-endpoints.js` with the `pipelines` endpoint group
- `frontend/static/desktop/protected/ccore/automation/automation.html` with the Pipeline dashboard card

## Validate generator files

```bash
python automation/factory/crud/frontend/validation/validate_generate_frontend.py --repo-root .
```

## Validate generated output after generation

```bash
python automation/factory/crud/frontend/validation/validate_generate_frontend.py --repo-root . --include-generated-output
```
