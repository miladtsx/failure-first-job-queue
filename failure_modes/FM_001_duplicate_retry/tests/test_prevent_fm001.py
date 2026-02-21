from failure_modes.FM_001_duplicate_retry.scenario import run_guarded_with_commit_boundary


def test_prevent_fm001_idempotent_commit_preserves_inv001():
    """FM_001 prevention: COMMITTED boundary no-ops duplicate retry attempts."""
    result = run_guarded_with_commit_boundary(
        lease_seconds=1,
        work_duration_seconds=2,
    )

    assert result.effects_count == 1
    assert result.committed_exec_id is not None

