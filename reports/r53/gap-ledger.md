# Gap Ledger

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

All PARTIALLY_MET and NOT_MET items from requirements-vs-actual-matrix.md.

## GAP-001 — Final Proof PASS 2 PENDING (REMEDIATED in R53)

- **Severity:** HIGH
- **Req:** REQ-GOV-003
- **Description:** R52 internal bundle proof had `PASS 2: PENDING` (self-referential impossibility)
- **Root cause:** ZIP cannot contain its own SHA; R52 left PENDING without producing external sidecar
- **Fix:** Sidecar proof protocol adopted. `write_sidecar_proof.py` + `--sidecar-proof` validator flag
- **Acceptance:** R53 closeout produces sidecar proof; `--sidecar-proof` validation passes
- **Status:** REMEDIATED_IN_R53
- **Taskcard:** TC-SIDECAR-PROOF-001

## GAP-002 — R52 Installed-Artifact Baseline Overclaim (REMEDIATED in R53)

- **Severity:** HIGH
- **Req:** REQ-PKG-001
- **Description:** R52 claimed `INSTALLED_ARTIFACT_BASELINE_CLEAN` but ZIP had no artifact files
- **Root cause:** Artifacts unchanged from R51; R52 referenced them but overclaimed clean baseline
- **Fix:** `installed-artifact-baseline-policy.md` created; R52 verdict corrected to `_PARTIAL`
- **Acceptance:** Policy document exists; future sprints use correct verdict suffix
- **Status:** REMEDIATED_IN_R53
- **Taskcard:** TC-ARTIFACT-BASELINE-POLICY-001

## GAP-003 — No Extracted-Bundle Installed-Wheel Smoke

- **Severity:** MEDIUM
- **Req:** REQ-PKG-002
- **Description:** No proof that Python wheels install correctly from extracted bundle
- **Root cause:** R52/R53 do not rebuild; extraction-based replay needs artifact files in bundle
- **Fix:** Future sprint: rebuild wheels; run extracted-bundle smoke
- **Status:** OPEN
- **Taskcard:** TC-INSTALLED-WHEEL-SMOKE-001

## GAP-004 — TC-0057: FODT Heading Preservation Not Implemented

- **Severity:** MEDIUM
- **Req:** REQ-PRES-002
- **Description:** FODT writer does not emit heading attributes on round-trip
- **Root cause:** Deferred R52→R53; R53 prioritized TC-0054 (formula)
- **Fix:** R54: FODT writer emit `text:outline-level` for heading blocks
- **Status:** OPEN
- **Taskcard:** TC-0057

## GAP-005 — TC-0058: FODT List Preservation Not Implemented

- **Severity:** MEDIUM
- **Req:** REQ-PRES-003
- **Description:** FODT writer does not emit list structure on round-trip
- **Fix:** R54: FODT writer emit `text:list` structure
- **Status:** OPEN
- **Taskcard:** TC-0058

## GAP-006 — TC-0059: FODT Table Preservation Not Implemented

- **Severity:** MEDIUM
- **Req:** REQ-PRES-004
- **Description:** FODT writer does not emit table structure on round-trip
- **Fix:** R54: FODT writer emit table elements
- **Status:** OPEN
- **Taskcard:** TC-0059

## GAP-007 — Agent Metrics Live Post Not Proven

- **Severity:** MEDIUM
- **Req:** REQ-AI-003
- **Description:** Agent Metrics only in fixture mode; no live post in R52/R53
- **Fix:** R54: live Agent Metrics post with HTTP evidence
- **Status:** OPEN

## GAP-008 — Phase Audit 4 Has 3 Open TCs

- **Severity:** MEDIUM
- **Req:** REQ-PHASE-001
- **Description:** TC-0054 closed by R53; TC-0057/0058/0059 still open
- **Fix:** R54: implement FODT heading preservation (TC-0057) minimum
- **Status:** OPEN
- **Taskcard:** TC-0057

## GAP-009 — FODT TXT Export Dogfooding Incomplete

- **Severity:** LOW
- **Req:** REQ-EXPORT-001
- **Description:** TXT exporter exists but no installed-wheel dogfooding proof
- **Fix:** R54: run FODT TXT smoke from installed wheel
- **Status:** OPEN

## GAP-010 — dotnet test Hangs in Current Environment

- **Severity:** LOW
- **Req:** REQ-DOTNET-001
- **Description:** `dotnet test src/net/fods/` returns no test results
- **Fix:** R54: investigate dotnet test invocation; document workaround
- **Status:** OPEN

## Taskcard Summary

| Taskcard | Gap | Status |
|----------|-----|--------|
| TC-SIDECAR-PROOF-001 | GAP-001 | REMEDIATED_IN_R53 |
| TC-ARTIFACT-BASELINE-POLICY-001 | GAP-002 | REMEDIATED_IN_R53 |
| TC-INSTALLED-WHEEL-SMOKE-001 | GAP-003 | OPEN |
| TC-0054 | — | CLOSED (R53) |
| TC-0057 | GAP-004, GAP-008 | OPEN |
| TC-0058 | GAP-005 | OPEN |
| TC-0059 | GAP-006 | OPEN |
