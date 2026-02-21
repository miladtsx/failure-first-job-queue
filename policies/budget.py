from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryBudget:
    """Deterministic retry budget used to cap retry storms."""

    max_attempts: int

    def allows(self, attempt: int) -> bool:
        return attempt <= self.max_attempts

