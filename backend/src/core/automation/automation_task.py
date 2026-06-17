"""
Automation task domain objects.

Responsibilities:
- Represent registered automation tasks as domain objects.
- Keep automation task metadata separate from raw registry JSON.
- Support the first script execution and visualization vertical slice.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationTask:
    task_id: str
    name: str
    description: str
    category: str
    status: str
    script_path: str
    config_path: str
