from __future__ import annotations

from dataclasses import dataclass

from faults.injectors import Faults
from runtime.clock import Clock
from runtime.queue import Queue
from runtime.store import Store


@dataclass(frozen=True)
class RuntimeFixture:
    """Deterministic in-memory runtime bundle for tests/scenarios."""

    clock: Clock
    store: Store
    queue: Queue
    faults: Faults


def make_runtime_fixture(*, lease_seconds: int, faults: Faults | None = None) -> RuntimeFixture:
    """Construct a minimal deterministic runtime.

    Centralizing this keeps setup consistent while preserving test readability.
    """
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=lease_seconds)
    return RuntimeFixture(clock=clock, store=store, queue=queue, faults=faults or Faults.none())

