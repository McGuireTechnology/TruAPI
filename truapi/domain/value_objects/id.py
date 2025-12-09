"""Domain value object for identifiers (ULID-backed).

Encapsulates ULID string creation and validation.
"""
from dataclasses import dataclass
from typing import Final

import ulid


@dataclass(frozen=True)
class ID:
    """Strongly-typed identifier value object."""

    value: str

    @classmethod
    def new(cls) -> "ID":
        # Create a new, time-sortable ULID string
        return cls(str(ulid.ULID()))

    @classmethod
    def from_str(cls, value: str) -> "ID":
        try:
            # Validate ULID format; raises if invalid
            ulid.ULID.from_str(value)
        except Exception as exc:
            raise ValueError("Invalid ULID format") from exc
        return cls(value)

    def __str__(self) -> str:  # pragma: no cover
        return self.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"ID('{self.value}')"


__all__: Final = ["ID"]
