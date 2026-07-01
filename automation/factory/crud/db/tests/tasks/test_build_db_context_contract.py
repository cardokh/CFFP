"""Legacy DB context task boundary tests.

The legacy postgres/build_db_context task was removed when PostgreSQL moved to
implementations/postgres. These tests now assert that the legacy folder has not
been reintroduced.
"""

from __future__ import annotations

from tests.support.db_test_paths import get_db_root


def test_legacy_postgres_build_db_context_folder_is_not_present() -> None:
    db_root = get_db_root()
    assert not (db_root / "postgres" / "build_db_context").exists()
