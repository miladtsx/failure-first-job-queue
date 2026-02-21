from failure_modes.template.scenario import run
from faults.injectors import Faults


def test_prevent_fmxxx_fix_preserves_invariants():
    faults = Faults(enforce_idempotent_commit=True)

    result = run(
        lease_seconds=1,
        work_duration_seconds=2,
        faults=faults,
    )

    # After the fix, the invariant-preserving behavior is asserted.
    assert result.effects_count == 1
    assert result.committed_exec_id is not None
