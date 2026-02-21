from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CircuitBreaker:
    """Minimal failure counter to expose containment decisions explicitly."""

    failure_threshold: int
    failures: int = 0

    def record_failure(self) -> None:
        self.failures += 1

    def reset(self) -> None:
        self.failures = 0

    @property
    def is_open(self) -> bool:
        return self.failures >= self.failure_threshold

