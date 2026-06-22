"""
CCore database infrastructure contracts.

Responsibilities:
- Define replaceable database/connection-provider abstractions.
- Keep repositories dependent on contracts instead of concrete database managers.
- Allow PostgreSQL, SQLite, test-double, or future pooled connection providers to be swapped.
"""

from typing import Any, Protocol


class DatabaseConnectionProviderProtocol(Protocol):
    def get_connection(self) -> Any:
        ...
