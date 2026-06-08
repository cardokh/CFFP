"""
Pytest path configuration.

Responsibilities:
- Ensure backend package imports work when tests are run.
- Keep test imports aligned with application imports such as src.api.route_dispatcher.
"""

import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()

BACKEND_ROOT = CURRENT_FILE.parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
