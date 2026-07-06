# Input

Human-authored project input consumed by the AI engine.

Task 02 treats PDF as the primary source-document format for the current CAutomation development path. DOCX and Markdown remain supported where configured, but PDF is the reference execution and validation path.

Required Pipeline Management contract inputs:

- `client/Project_Client_Contract.pdf` - required project-level client contract.
- `engineering/Project_Engineering_Contract.pdf` - required project-level engineering contract.
- `modules/pipeline_management/Software_Requirements_Specification.pdf` - required module-level WHAT/SRS contract.
- `modules/pipeline_management/Architecture_and_Technical_Specification.pdf` - required module-level HOW/ATS contract.

Optional future contract profiles, such as UI, database, API, UX, and security specifications, must be declared and enabled in the Pipeline 01 configuration before Task 02 consumes them.
