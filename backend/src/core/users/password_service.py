"""
Password security service.

Responsibilities:
- Hash raw passwords before storage
- Verify passwords during authentication

This service isolates password security logic from the rest
of the authentication workflow.
"""

import bcrypt


class PasswordService:
    def hash_password(self, raw_password: str) -> str:
        hashed = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            bcrypt.gensalt(),
        )

        return hashed.decode("utf-8")

    def verify_password(
        self,
        raw_password: str,
        stored_hash: str,
    ) -> bool:
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )
