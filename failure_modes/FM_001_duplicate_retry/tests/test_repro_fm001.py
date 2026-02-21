from failure_modes.FM_001_duplicate_retry.scenario import run_known_broken_baseline


def test_repro_fm001_duplicate_effect_occurs_without_commit_boundary():
    """FM_001 repro: retry after timeout causes duplicate logical effect (violates INV_001)."""
    result = run_known_broken_baseline(
        lease_seconds=1,
        work_duration_seconds=2,
    )

    assert result.effects_count == 2
    assert result.committed_exec_id is not None

