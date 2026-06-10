# Current State Review
# Sprint: product-progress-rnext
# Generated: 2026-06-09

## Git State
- HEAD: e382e5fd8e65bc146c0821602cb8fb1ecfab982c
- Commit: feat(r94-r116+)
- Modified (not committed): toml_codec.py, __init__.py, ledger, supervisor reports

## Package 153 Changes Present?
- YES: src/python/toml/toml_codec.py — get_value, merge_toml, to_json_str added
- YES: src/python/toml/__init__.py — exports updated
- FODG: Already has all 21 functions from full-hardening-rnext sprint

## FODG Status
- Source: src/python/fodg/fodg_codec.py (704 lines)
- add_page: dual-signature (str or dict), raises TypeError for non-str/non-dict (int etc.)
- FAILING TEST from sprint prompt: test_r138_fodg_add_page::test_type_error_non_dict_page
  - STATUS: NOW PASSING (188/188 FODG tests pass with venv pytest)
  - Root cause: test passes int (12345) → add_page raises TypeError for non-str non-dict ✓
  - R152 test: passes "string" → works ✓
  - No FODG code change needed

## TOML Status
- Source: src/python/toml/toml_codec.py
- Functions: probe_toml, load_toml, write_toml, get_keys, roundtrip, get_value, merge_toml, to_json_str
- Tests: 16 files (30 existing + 14 new from last sprint) — all pass
- MISSING: set_value, list_sections

## Selected Product Gaps
- selected-product-task.json: {selected: null, no_safe_task_found: true} — STALE
- selected-product-gaps.json: NOT FOUND

## Action Queue
- reports/capability-layer/action-queue.json: 1 action (ACT-UPDATE-POC-TARGETS) — STALE
- Only 1 action present; needs refresh with real product tasks

## Capability Gap Ledger
- reports/capability-layer/gap-ledger.json: 0 gaps
- 513 total records (125 commercial + 388 FOSS)
- Generator ran successfully in last sprint

## Product-Code Ledger
- reports/r90/product-code-change-ledger.json: 176 entries
- Last entry: FRFH-TOML-001 (added last sprint)

## poc-targets.yaml
- Present: product-capability-matrix/poc-targets.yaml
- TOML not yet in matrix, FODG entry may be stale

## Focused Tests Baseline
- FODG: 188/188 PASS (was 187/188 — now fully resolved)
- TOML: 30/30 PASS (16 + 14 new)
- TSV: passing (37 files, ~160 tests)
- NDJSON: passing (28 files, ~140 tests)

## Unsafe Wording Check
- action-queue.json: advisory_only: true, no push/commit wording ✓
- next-sprint.md: needs inspection

## Decision
- FODG: NO REPAIR NEEDED — already 188/188
- TOML: Add set_value + list_sections
- Additional: Add NDJSON and SYLK focused improvements
- Gaps: Refresh action queue with real tasks
