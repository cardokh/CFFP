"""Wiring updates required by generated frontend CRUD modules."""
from __future__ import annotations

from .config_loader import EntityConfig


PIPELINE_CARD = '''
                            <a class="automation-dashboard-card"
                                href="/desktop/protected/ccore/automation/pipelines/pipelines.html">
                                <span class="automation-dashboard-card-icon">🔁</span>
                                <h3>CCore Automation Pipelines</h3>
                                <p>Create, update, and delete PostgreSQL-backed CCore pipeline records.</p>
                                <span class="automation-dashboard-card-action">Open module →</span>
                            </a>
'''


def add_dashboard_card(content: str) -> tuple[str, bool]:
    if "/desktop/protected/ccore/automation/pipelines/pipelines.html" in content:
        return content, False

    tasks_marker = '''                            <a class="automation-dashboard-card"
                                href="/desktop/protected/ccore/automation/tasks/tasks.html">'''
    tasks_start = content.find(tasks_marker)

    if tasks_start >= 0:
        return content[:tasks_start] + PIPELINE_CARD + "\n" + content[tasks_start:], True

    grid_marker = '<div class="automation-dashboard-grid" aria-label="CCore modules">'
    grid_start = content.find(grid_marker)

    if grid_start < 0:
        raise ValueError("Could not find automation dashboard grid insertion point.")

    insert_at = grid_start + len(grid_marker)
    return content[:insert_at] + "\n" + PIPELINE_CARD + content[insert_at:], True


def add_api_endpoints(content: str, entity: EntityConfig) -> tuple[str, bool]:
    if f"{entity.api_key}: {{" in content:
        return content, False

    block = f'''

    {entity.api_key}: {{
        list: "{entity.api_base_path}",
        create: "{entity.api_base_path}",
        statuses: "{entity.api_status_path}",

        byId({entity.id_field}) {{
            return `{entity.api_base_path}/${{encodeURIComponent({entity.id_field})}}`;
        }}
    }},'''

    tasks_marker = "\n    tasks: {"
    tasks_start = content.find(tasks_marker)

    if tasks_start >= 0:
        tasks_end = content.find("\n    },", tasks_start)
        if tasks_end < 0:
            raise ValueError("Could not find Tasks endpoint block end.")
        tasks_end += len("\n    },")
        return content[:tasks_end] + block + content[tasks_end:], True

    object_end = content.rfind("\n};")
    if object_end < 0:
        raise ValueError("Could not find CCORE_API_ENDPOINTS object end.")

    return content[:object_end] + block + content[object_end:], True
