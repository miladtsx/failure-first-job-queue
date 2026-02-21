# FM_XXX — <short title>

## Description
One sentence describing the failure mode in plain language.

## Trigger
The concrete condition(s) that cause this failure mode.
- trigger 1
- trigger 2

## Preconditions
What must be true in the system for this failure mode to be possible.
- precondition 1
- precondition 2

## Failure mechanism (step-by-step)
Numbered steps describing the sequence that produces the failure.
1. ...
2. ...
3. ...

## Symptoms
What you would see in logs/metrics/state.
- symptom 1
- symptom 2

## Violated invariants
List the invariant IDs from [`invariants`](../../docs/01_invariants.md).
- INV_XXX — ...
- INV_YYY — ...

## Detection
How the system should detect this failure mode.
- signals/metrics/log patterns
- audit queries / reconciliation checks

## Recovery / prevention strategy
How the system should prevent the failure or recover correctness.
- prevention approach
- recovery approach

## Acceptance criteria
The minimum set of tests that must pass.
- `test_repro_fmxxx.py` demonstrates the failure in baseline/broken config
- `test_prevent_fmxxx.py` proves the fix preserves invariants

## Notes
Constraints, trade-offs, and “what we are intentionally not solving here”.
