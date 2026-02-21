from failure_modes.template.scenario import run
from faults.injectors import Faults


def test_repro_fmxxx_baseline_shows_failure():
    faults = Faults.none()

    result = run(
        lease_seconds=1,
        work_duration_seconds=2,  # make lease expire
        faults=faults,
    )

    # This assertion should capture the failure's manifestation.
    # Example: duplicated effects.
    assert result.effects_count == 2
