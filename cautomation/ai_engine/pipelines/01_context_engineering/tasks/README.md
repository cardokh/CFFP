# 01 Context Engineering Tasks

Tasks are the executable units of this pipeline.

Current task:

```text
context_engineering/
├── context_engineering.py
├── config/
│   └── context_engineering.json
└── output/
```

Each task must follow the repository scripting infrastructure:

- extend `scripts.shared.base_script.BaseScript`,
- read settings from its local JSON config file,
- avoid hard-coded project/module/file paths,
- write execution reports to its own output folder,
- write domain artifacts only to configured output locations.
