# Amended Execution Plan
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Generated: 2026-06-05

## Executive Summary

This plan amends the R119 mega-train sprint based on discovery that the previous sprint
(FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001) already completed:
- FormatFactory.Csv reusable writer (LANE C original objective)
- FODS CSV integration via reusable writer (LANE D original objective)
- FormatFactory.Html, FormatFactory.Txt, FormatFactory.Markdown writers
- BLOCKED_GAP_IDS is now frozenset() — all 4 blocked gaps unblocked

The sprint therefore AMENDS focus to:
1. VERIFY existing implementation (not re-implement)
2. Repair Spec Authority R3C closure (confirm snapshot, document)
3. Repair RCA R1 evidence quality (add raw logs, sample outputs, git status)
4. Fix RCA gap queue policy (ensure re-tested with unblocked writers)
5. Document state transitions and generate next sprint

---

## What Was Kept from Spec Authority R3C (Bundle 98)
- All 7/8 ACCEPTED_VERIFIED work items preserved
- RCA input snapshot confirmed: `reports/spec-authority-r3-closure-repair/rca-r2-input-packet.json`
- ODF R4 plan preserved: `reports/spec-authority-r3-closure-repair/odf-r4-depth-plan.md`
- review-package-proof.md SHA: `cda78872d5b98e5e1b5634257700c63ef452b3111f9153d58d827acab409e96d`
- Spec authority test suite: 163/163 PASS — no regressions

## What Was Kept from RCA R1 (Bundle 99)
- 57/57 RCA tests pass (tests/requirement_capability_authority/)
- Proof graph structure: 81 nodes, 102 edges
- 5 pilots run (Netpbm, FODS, FODT, ZST, DIF)
- Gap queue policy fix from R2: architecture-blocked claims → TargetWriterArchitecture lane
- `BLOCKED_GAP_IDS = frozenset()` (writers now built)

## Contradictions Being Repaired

### C1: Bundle 98 — review-package-proof.md "missing" from materialized evidence
- **Root cause:** proof file is written AFTER the ZIP (by design per protocol)
- **Resolution:** Confirm existing proof file is present and valid. No code change needed.
- **Status:** REPAIRED IN R3C — confirmed this sprint

### C2: Bundle 99 — FODS/FODT export routing to Mainstream-Dogfood (R1)
- **Root cause:** mainstream_gap_queue.py did not detect architecture-blocked claims
- **Resolution:** Fixed in R2 sprint (`_build_entry()` detects arch-blocked via `blocked_by` edge)
- **Status:** REPAIRED IN R2 — confirmed this sprint via select_poc_gaps.py BLOCKED_GAP_IDS={}

### C3: Bundle 99 — evidence_quality_score 0.12
- **Root cause:** `tests_supporting` field was empty; inspector reads only that field for test files
- **Resolution:** This sprint adds proper `tests_supporting` pointers in evidence declaration
- **Status:** REPAIRING this sprint

### C4: Bundle 99 — missing raw logs / sample outputs in anti-skip-detected paths
- **Root cause:** Logs and outputs placed in reports dir, not `.local/evidences/` subtree
- **Resolution:** This sprint places artifacts in correct paths
- **Status:** REPAIRING this sprint

## Implementation Lanes Added

### LANE C (Amended): Verification Mode
- Previous sprint built the writer. This sprint VERIFIES:
  - 15/15 CSV writer tests pass ✓
  - 547/547 FODS tests pass (including CSV integration) ✓
  - API is documented in `target-writer-csv/csv-writer-api-summary.md` (this sprint)
  - Registry patch proposed (this sprint)

### LANE D (Amended): Verification Mode
- FODS CSV exporter already delegates to `CsvWriter.WriteRowsToFile()` / `CsvWriter.WriteRows()`
- Dogfood sample output produced this sprint (verify export runs, capture output artifact)
- Capability delta proposal written this sprint

### LANE E (Amended): Document existing HTML/Txt/Markdown writers
- All 3 writers exist. This sprint documents their API and produces work-ahead plans for:
  - FODT TXT integration wiring
  - FODT Markdown integration wiring
  - FODS HTML integration wiring

### LANE F (Amended): Re-test gap queue with unblocked writers
- `BLOCKED_GAP_IDS = frozenset()` confirmed
- Run existing export policy tests
- Add R119-specific test confirming no regressions

### LANE G: Evidence detection hardening
- Add targeted test for anti-skip raw log / sample output detection
- Add review-package-proof.md requirement test

## What Is Explicitly Not Being Touched
- product-capability-matrix/poc-targets.yaml (read-only this sprint)
- registry/format-registry.yaml (proposed patches only)
- FODT integration source (separate sprint with tests)
- FODS HTML integration source (separate sprint with tests)
- Any gate approval
- Any git push or commit

## Success Criteria
1. FODS CSV: reusable writer verified, tests pass, dogfood sample exists
2. Spec R3C: snapshot confirmed, closure documented
3. RCA R1: evidence quality repaired (tests_supporting populated, raw logs/samples present)
4. Gap queue: BLOCKED_GAP_IDS=frozenset() confirmed by test
5. Evidence bundle: complete with all required artifacts
6. No overclaims: HTML/Markdown/TXT remain classified as separate (wired but not all gap-tested)
