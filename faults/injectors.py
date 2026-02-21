from dataclasses import dataclass


@dataclass(frozen=True)
class Faults:
    """Deterministic fault toggles used by failure-mode scenarios."""

    crash_before_commit: bool = False
    crash_after_commit_before_done: bool = False
    enforce_idempotent_commit: bool = False

    @staticmethod
    def none() -> "Faults":
        return Faults()
