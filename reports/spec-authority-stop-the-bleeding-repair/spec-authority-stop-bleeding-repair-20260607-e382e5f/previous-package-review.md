# Previous Package Review
# Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-REPAIR-AND-ENFORCEMENT-001
# Run: spec-authority-stop-bleeding-repair-20260607-e382e5f
# Reviewing: stop-the-bleeding-20260607-e382e5f
# Date: 2026-06-07

## Summary of previous sprint outcome

Sprint ID: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001
autonomous-cycle exit: 0
Items accepted: 5/5
Autonomous Continue: True (but stop reason = evidence quality 0% verified)

## Defects recorded

### DEF-001 — spec_fact_refs schema exists but not wired into real evidence validation
The schema at `schemas/evidence/spec-fact-refs.schema.json` exists as a standalone
JSON schema document. It is NOT called by `evidence_declaration.py`,
`grade_declared_work.py`, or `autonomous_cycle.py`. Enforcement is documentation-only.
A declaration with PRODUCT_SOURCE work and no spec_fact_refs/exception was accepted.
Severity: CRITICAL
Fix: TCA-R001

### DEF-002 — no tests run (tests_run=0)
The evidence declaration had tests_run=0 and test_results all zeros.
No enforcement tests exist. No regression tests exist for this sprint.
This means the BLOCKING gate has no automated proof.
Severity: CRITICAL
Fix: TCA-R002

### DEF-003 — anti-skip all_pass=false
Anti-skip check produced 3 violations: missing_raw_logs, missing_lane_ledger,
missing_sample_outputs (MEDIUM/LOW). All_pass was false.
Severity: MEDIUM
Fix: TCA-R006

### DEF-004 — adoption compliance FAIL_MISSING_TRANSCRIPTS
All 5 work items had adoption compliance FAIL because no skill transcripts
were provided. No exemptions were filed for non-skill work.
Severity: MEDIUM
Fix: TCA-R006

### DEF-005 — accepted-with-limitations items produced no rework items
All 5 items were accepted with path-only evidence (no concrete proof dimension).
ACCEPTED_WITH_LIMITATIONS should generate rework items for the next sprint
but the supervisor generated a mainstream next sprint instead.
Severity: HIGH
Fix: TCA-R003, TCA-R007

### DEF-006 — global next sprint points to mainstream product work
The generated `reports/supervisor/next-sprint.md` points to product deepening
(mainstream formats, Gate 11 prep) rather than spec-authority enforcement work.
This continues product expansion before the enforcement gate is active.
Severity: CRITICAL
Fix: TCA-R007

### DEF-007 — Gnumeric classified as no_public_spec_available despite XSD authority
Gnumeric has `gnumeric.xsd` in `.local/spec-cache/gnumeric/v10/`. This XSD is
a schema authority document. The bypass ledger incorrectly used
`no_public_spec_available` instead of `schema_authority_available`.
Severity: MEDIUM
Fix: TCA-R005

### DEF-008 — no package SHA manifest
The declaration review package was built but no SHA256-MANIFEST.txt was
included in the sprint reports. The package hash was reported as a single
sha256 sum of the ZIP file, not a manifest of individual files.
Severity: LOW
Fix: TCA-R008

### DEF-009 — no lane ledger
No lane execution ledger was produced during the sprint.
Required by anti-skip checker.
Severity: MEDIUM
Fix: TCA-R006

### DEF-010 — no negative tests proving missing spec_fact_refs blocks product work
The core deliverable of the stop-the-bleeding sprint was enforcement.
No automated tests exist proving that a PRODUCT_SOURCE declaration without
spec_fact_refs or exception is blocked. The enforcement is therefore unverifiable.
Severity: CRITICAL
Fix: TCA-R002

## Defect severity summary

CRITICAL: DEF-001, DEF-002, DEF-006, DEF-010 (4)
HIGH:     DEF-005 (1)
MEDIUM:   DEF-003, DEF-004, DEF-007, DEF-009 (4)
LOW:      DEF-008 (1)
