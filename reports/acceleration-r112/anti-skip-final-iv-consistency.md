# Anti-Skip / Final-IV Consistency — R112

## Classification Model
Anti-skip violations are now separated into 4 tiers:
1. **blocking_failures** (critical): Must stop continuation. Examples: stale_gaps, wrong_stream_gaps
2. **downgrade_failures** (high): Downgrade verdict. Examples: generic_prompt, test_count_regression
3. **non_blocking_warnings** (medium): Caveat, does not block. Examples: wrong_stream_next_sprint
4. **informational_notes** (low): Info only. Examples: missing_sample_outputs, stream_local_authority

## Consistency Rules
- If anti-skip all_pass=false with only low/medium violations:
  - Final IV may say "PASS with non-blocking caveats"
  - Quota tracker must list the caveats explicitly
  - Continuation state: YES_WITH_LIMITATIONS (not plain YES)
- If anti-skip has critical/high violations:
  - Final IV must report them as failures
  - Continuation state: NO_*

## R112 Verification
- TestAntiskipFinalIVConsistency: 5 tests proving classification works correctly
