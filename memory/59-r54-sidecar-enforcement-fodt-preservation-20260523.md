---
memory_id: 59
sprint: FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
date: 2026-05-23
visibility: internal
publish_allowed: false
---

# R54 — Sidecar Enforcement + FODT Preservation + Phase Audit 5

## Sprint Metadata

- **Sprint ID:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
- **Date:** 2026-05-23
- **Verdict:** R54_STATE_SIDECAR_ENFORCEMENT_FODT_PRESERVATION_PARTIAL

## Key Accomplishments

### Lane 1: R53 Independent Verification
- R53 classified: `R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL_ACCEPTED_WITH_R54_REPAIR_REQUIRED`
- 7 defects found: TC mislabeling (TC-0057/0058/0059), heading false claim, gap ledger, sidecar optional, write_sidecar trusted --validation-result
- Preflight: GO decision after defect catalog

### Lane 2: Sidecar Enforcement (fail-closed)
- `validate_evidence_bundle.py`: added `check_sidecar_required()` and `check_sidecar_filename_match()`
- New contract fields: `sidecar_required`, `final_proof_policy: external_sidecar`
- Verdict tokens that auto-require sidecar: SELF_VERIFYING, BASELINE_CLEAN, SELF_CONTAINED, INSTALLED_ARTIFACT_BASELINE
- `write_sidecar_proof.py`: added `--verify` flag (runs actual validation before writing sidecar)
- 18 tests PASS: `tests/evidence/test_r54_sidecar_required_enforcement.py`

### Lane 3: Artifact Policy Enforcement
- `validate_evidence_bundle.py`: added `check_installed_artifact_policy()`
- New contract field: `installed_artifact_policy` with values: `none` / `external_ref` / `self_contained`
- `external_ref` requires `prior_bundle_sha256:` and `prior_bundle_filename:` in package-artifacts-manifest
- `self_contained` requires actual .whl/.tar.gz/.nupkg files in bundle
- 11 tests PASS: `tests/evidence/test_r54_artifact_policy.py`

### Lane 4: Phase Audit 4 Truth Repair
- Corrected TC mislabeling: TC-0057=inline spans, TC-0058=table, TC-0059=list
- Confirmed heading preservation PASS since R49 (R53 false NOT_MET corrected)
- Report: `reports/r54/phase-audit-4-truth-repair.md`

### Lane 5: Taskcard State Machine Repair
- TC-0054 closed: `taskcards/TC-0054-formula-preservation-fods.md` → Status: CLOSED_VERIFIED
- Closure evidence: R53, 7 tests PASS in test_r53_formula_preservation.py

### Lane 6: FODT Preservation (TC-0059/TC-0058 partial advance)
- `src/python/fodt/writer.py`: added `_write_list()` and `_write_table()`
- List round-trip: `text:list` → `text:list-item` → `text:p`; parsed back correctly
- Table round-trip: `table:table` → `table:table-row` → `table:table-cell` → `text:p`
- Table names preserved via `table:name` attribute
- Known limitation: document ordering between blocks/lists/tables not preserved (separate sequences; R55 deferred)
- TC-0057 (inline spans): OPEN — `text:span` not emitted; 1 test documents limitation
- 21 tests PASS: `tests/python/fodt/test_r54_fodt_preservation.py`

### Lane 7: FODS Formula Documentation
- `src/python/fods/writer.py` docstring updated to reflect TC-0054 closed
- Capability level line updated: "formulas (round-trip only)" noted

### Lane 8: Phase Audit 5
- CONDITIONAL_PASS_WITH_FODT_GAPS
- FODS: full PASS; FODT headings: PASS; lists/tables: PARTIAL_PASS; spans: OPEN
- Report: `reports/r54/phase-audit-5-product-mapping.md`

### Lane 9: .NET Bounded Verification
- DOTNET_BOUNDED_VERIFICATION: PASS — no regressions from Python R54 work
- Gate 11 G11-G remains NOT_STARTED; commercial_product_ready: false
- Report: `reports/r54/dotnet-bounded-verification.md`

### Lane 10: Artifact Explicit None Claim
- R54 policy: `installed_artifact_policy: none`
- No artifact rebuild; prior baseline is R51 (6 Python packages)
- Report: `reports/r54/package-artifact-policy.md`

### Lane 11: AI Governance Telemetry Proof
- AI_GOVERNANCE_R54: PASS (0 live AI calls, 0 ungoverned calls)
- Report: `reports/r54/ai-usage-telemetry-proof.md`

### Lane 12: Invariants INV-006..010
- Added 5 new invariants to `tools/evidence/check_repo_invariants.py`
- INV-006: sidecar .sha256-proof.json not git-tracked
- INV-007: latest sprint's final-verdict.md has no stale placeholder phrases
- INV-008: latest contract's min_metadata_count is parseable and >= 1
- INV-009: fodt/writer.py defines both `_write_list` and `_write_table`
- INV-010: all CLOSED_VERIFIED taskcards have closure section/date evidence
- 22 tests PASS: `tests/invariants/test_r54_invariants.py`
- All 10 invariants (INV-001..010) PASS on real repo

### Lane 13: Memory Sync
- `memory/59-r54-*.md` created (this file)
- `memory/00-index.md` updated with R53+R54 rows

## Test Summary

- Lane 2 sidecar enforcement: 18 tests PASS
- Lane 3 artifact policy: 11 tests PASS
- Lane 6 FODT preservation: 21 tests PASS (5 heading + 7 list + 8 table + 1 span-open)
- Lane 12 invariants: 22 tests PASS
- **New tests total: 72**

## Known Limitations / Deferred to R55

- TC-0057 (FODT inline spans): OPEN — requires parser + writer changes
- FODT document ordering: blocks/lists/tables in separate neutral model sequences; ordering not preserved
- dotnet test_build_report_all_built: pre-existing count mismatch (unchanged)
- AI acceleration round 3: deferred
- Artifact rebuild: deferred until TC-0057/0058/0059 fully closed

## Files Changed

**New files:**
- `tests/evidence/test_r54_sidecar_required_enforcement.py`
- `tests/evidence/test_r54_artifact_policy.py`
- `tests/python/fodt/test_r54_fodt_preservation.py`
- `tests/invariants/test_r54_invariants.py`
- `reports/r54/00-preflight.md`
- `reports/r54/lane-ownership.md`
- `reports/r54/work-ahead-policy.md`
- `reports/r54/risk-register.md`
- `reports/r54/r53-independent-verification.md`
- `reports/r54/phase-audit-4-truth-repair.md`
- `reports/r54/phase-audit-5-product-mapping.md`
- `reports/r54/dotnet-bounded-verification.md`
- `reports/r54/package-artifact-policy.md`
- `reports/r54/ai-usage-telemetry-proof.md`
- `memory/59-r54-sidecar-enforcement-fodt-preservation-20260523.md` (this file)

**Modified files:**
- `tools/evidence/validate_evidence_bundle.py` (sidecar enforcement + artifact policy)
- `tools/evidence/write_sidecar_proof.py` (--verify flag)
- `tools/evidence/check_repo_invariants.py` (INV-006..010)
- `src/python/fodt/writer.py` (_write_list, _write_table, table namespace, R54 docstring)
- `src/python/fods/writer.py` (TC-0054 docstring update)
- `taskcards/TC-0054-formula-preservation-fods.md` (CLOSED_VERIFIED)
- `memory/00-index.md` (R53+R54 rows)
- `memory/MEMORY.md` (current state update)
