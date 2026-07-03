# Pipelines

Pipelines are isolated stages in the AI-assisted software development flow.

Each pipeline is responsible for converting a defined set of inputs into a defined set of outputs. A pipeline must not read arbitrary repository content or depend on conversation history.

## Current Pipeline Sequence

```text
00_shared
01_context_engineering
02_db
03_backend
04_frontend
05_testing
06_deployment
```

`01_context_engineering` is the first real reusable pipeline. It prepares validated context for downstream generation pipelines.

The later pipeline folders currently describe intended responsibilities and may evolve as the context engineering contract becomes stable.
