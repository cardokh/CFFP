import sqlite3
from pathlib import Path

"""
Database infrastructure manager.

Responsibilities:
- Store the configured database path
- Create SQLite database connections

This class belongs to the infrastructure layer and isolates
low-level database connection handling from the rest of the application.
"""


class DatabaseManager:
    def __init__(self, db_file: str = "auth.db"):
        self.db_path = Path(db_file)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
