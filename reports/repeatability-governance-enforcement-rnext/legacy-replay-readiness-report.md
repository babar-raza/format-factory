# Legacy Replay Readiness Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: J (GRE-TC-010)
# Date: 2026-06-08

## 4 Backfilled Functions Verified

### set_cell_value (gnumeric)

Source file: src/python/gnumeric/gnumeric_codec.py
Symbol verified: set_cell_value function exists (tests pass in tests/python/gnumeric/)
Idempotency key: aff66c999800c221ffe346134519aae0b838cde1ec9cc66fbcc7b578ed81fbf9
Key formula: SHA256("gnumeric|set_cell_value|set_cell_value|MANUAL|src/python/gnumeric/gnumeric_codec.py")
Sidecar: .local/attribution/gnumeric/gnumeric_codec.py.attribution.yaml — EXISTS
Claim: LEGACY_BACKFILLED (correct — cannot claim REPEATABLE)
may_claim_repeatable: false
may_claim_autonomous: false

### get_headers (tsv)

Source file: src/python/tsv/tsv_parser.py
Symbol verified: get_headers function exists (tests pass in tests/python/tsv/)
Idempotency key: 569a341630a9d69e9c97ce6a5e88ca6b5f78b0a4f18d9a3b7d5be0e52f3b9c11
Key formula: SHA256("tsv|get_headers|get_headers|MANUAL|src/python/tsv/tsv_parser.py")
Sidecar: .local/attribution/tsv/tsv_parser.py.attribution.yaml — EXISTS
Claim: LEGACY_BACKFILLED
may_claim_repeatable: false

### get_paragraph (abw)

Source file: src/python/abw/abw_codec.py
Symbol verified: get_paragraph function exists (tests pass in tests/python/abw/)
Idempotency key: 7feeaa437fd92f2fc36c75e42d7805edba656dce94b7f68681bc3dc66c367d3a
Key formula: SHA256("abw|get_paragraph|get_paragraph|MANUAL|src/python/abw/abw_codec.py")
Sidecar: .local/attribution/abw/abw_codec.py.attribution.yaml — EXISTS
Claim: LEGACY_BACKFILLED
may_claim_repeatable: false

### export_to_csv (ndjson)

Source file: src/python/ndjson/ndjson_codec.py
Symbol verified: export_to_csv function exists (tests pass in tests/python/ndjson/)
Note: ndjson_codec.py is UNTRACKED in git (??) — must be included in next commit
Idempotency key: 9c6c27982d18897bdd3116696dc0ac0ba625f2f6debe12e688ebdc98b9bea505
Key formula: SHA256("ndjson|export_to_csv|export_to_csv|MANUAL|src/python/ndjson/ndjson_codec.py")
Sidecar: .local/attribution/ndjson/ndjson_codec.py.attribution.yaml — EXISTS
Claim: LEGACY_BACKFILLED
may_claim_repeatable: false

## GR-REPLAY Taskcard Readiness

All 4 GR-REPLAY taskcards (GR-REPLAY-001..004) have been upgraded with:

### Required for replay readiness (all present in taskcards)
- `idempotency_key`: matches sidecar (verified by integration test)
- `sidecar_attribution_path`: correct path
- `current_state`: BACKFILLED_LEGACY_ACCEPTED
- `target_state`: REPLAY_RECIPE_RECORDED
- `target_claim`: REPLAYABLE_NOT_YET_REPLAYED
- `files_to_create`: replay recipe path specified

### Still needed before replay execution
- `skill_candidate`: which skill to use for replay
- `replay_inputs`: exact inputs to reconstruct function
- `expected_diff_behavior`: NO_OP or EQUIVALENT_DIFF
- `validation_commands`: exact pytest invocations
- `stop_conditions`: when to abort replay

These fields are NOT yet in the taskcards. They should be added by the replay
execution sprint before executing any replay.

## Stop Conditions for Replay Execution

Do NOT execute replay until:
1. All 10 governance validators are wired into autonomous-cycle (DONE this sprint)
2. Governance validators produce 0 FAIL results for the replay declaration
3. AGENTS.md AE2-compliant rollback plan is documented
4. Source diff capture is planned (before_sha256 + after_sha256)
5. A dry-run fixture test confirms the replay infrastructure works

## Honest Status

Current status: LEGACY_BACKFILLED (not REPLAYABLE)
Next status after replay recipe written: REPLAYABLE_NOT_YET_REPLAYED
Status after replay executed and verified: REPLAYED_AND_PROVEN (goal)

No false repeatability claims are made. The 4 functions WORK but their implementation
cannot be reproduced from declared artifacts alone.
