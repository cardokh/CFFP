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
    marker = '''                            <a class="automation-dashboard-card"
                                href="/desktop/protected/ccore/automation/metrics/metrics.html">'''
    start = content.find(marker)
    if start < 0:
        raise ValueError("Could not find Metrics dashboard card insertion point.")
    end = content.find("                            </a>", start)
    if end < 0:
        raise ValueError("Could not find Metrics dashboard card end.")
    end += len("                            </a>")
    return content[:end] + "\n" + PIPELINE_CARD + content[end:], True


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
    marker = "\n    metrics: {"
    index = content.find(marker)
    if index < 0:
        raise ValueError("Could not find Metrics endpoint insertion point.")
    metrics_end = content.find("\n    },", index)
    if metrics_end < 0:
        raise ValueError("Could not find Metrics endpoint block end.")
    metrics_end += len("\n    },")
    return content[:metrics_end] + block + content[metrics_end:], True
