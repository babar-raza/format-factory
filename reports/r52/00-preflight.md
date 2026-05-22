# R52 Preflight

**Sprint:** FORMAT-FACTORY-R52-STATE-CONSISTENT-INSTALLED-ARTIFACT-BASELINE-CLEAN-001
**Run number:** R52
**Date:** 2026-05-22
**Prior sprint verdict:** R51_INSTALLED_ARTIFACT_BASELINE_AND_AI_ACCELERATION_COMPLETE

## R51 Classification

R51 was classified as `R51_INSTALLED_ARTIFACT_PROGRESS_REAL_BUT_STATE_AND_FINAL_PROOF_CONTRADICT` due to:

1. State snapshot returning `verdict: unknown` for R51 — `state_snapshot.py` regex did not handle R51's `## Verdict + backtick code-block` format
2. `validate_evidence_bundle.py` validator not detecting state/verdict contradiction
3. `final-bundle-validation-proof.txt` in R51 metadata claimed a SHA that became stale after validator fixes required rebuilding
4. `validation-command-log.txt` contained `Pass 1: PENDING` / `Pass 2: PENDING` stale markers
5. `build_evidence_bundle.py` wrote `"Pass 2 pre-proof build in progress..."` which matched `PROOF_FILE_PLACEHOLDER_PATTERNS` for `"IN PROGRESS"`, breaking auto_proof tests

## R52 Scope

**Lane 1A:** R51 state verdict parser repair (state_snapshot.py Format C support)
**Lane 1B:** Validator: `_parse_verdict_from_text()` helper + code-block format support
**Lane 1C:** Validator: `check_state_verdict_agreement()` — scan bundle for final-verdict.md, INV-003 false-blocker detection, stale-state detection
**Lane 2A:** Validator: `check_proof_sha_consistency()` — warn when proof SHA != actual bundle SHA
**Lane 2B:** Validator: `COMMAND_LOG_STALE_PATTERNS` extended (Pass 1/2 PENDING, to be completed)
**Lane 2C:** Validator: `PENDING_SCAN_SKIP_FILES` — skip git-log.txt/git-status files in PENDING scan
**Lane 2D:** Builder: fix `"Pass 2 pre-proof build in progress..."` → `"computing bundle metrics"` (not a placeholder pattern)
**Lane 2E:** Validator: `check_proof_file_finality()` — auto-proof transient placeholder exclusion
**Lane 3A:** 19 R52 guard tests (`tests/evidence/test_r52_validator_hardening.py`)
**Lane 3B:** 16 R51 retroactive guard tests (`tests/evidence/test_r51_validator_hardening.py`)
**Lane 3C:** 9 state snapshot guard tests added to `tests/state/test_state_snapshot.py`
**Lane 3D:** test_r28 exclusion: 2-pass protocol narrative not flagged as stale PENDING
**Lane 3E:** test_r49 auto-proof transient placeholder test preserved (no longer false-positive)

## R52 Deferred

- FODS formula preservation (TC-0054) — deferred to R53
- FODT structure preservation (TC-0057–0059) — deferred to R53
- FODT TXT/Markdown export — deferred to R53
- AI acceleration round 3 — deferred to R53
- Phase Audit 5 planning — deferred to R53
- Physical invariants matrix — deferred to R53
