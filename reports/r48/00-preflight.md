# R48 Preflight

**Sprint:** FORMAT-FACTORY-R48-ARTIFACT-RC-CLEAN-CLOSEOUT-AND-PHASE-AUDIT-COMPLETION-001
**Date:** 2026-05-22
**Run Number:** R48 (auto-detected — r47 is latest in reports/ and contracts/)
**Supersedes:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001

---

## Environment

| Item | Value |
|------|-------|
| Branch | main |
| HEAD (before R48) | da02a5f |
| Python | 3.13.2 |
| dotnet SDK | 10.0.204 |
| Platform | Windows 11 Pro 10.0.26200 |
| .git present | YES |

---

## R47 Closeout Defect — Confirmed

**`validate_evidence_bundle.py --check-no-pending` against R47 bundle:**
```
No-PENDING check (FAIL): 1 repo/reports final-verdict PENDING marker(s)
ERRORS:
  - R46: PENDING marker in bundled final-verdict 'repo/reports/r47/final-verdict.md':
    'BUNDLE_VALIDATION: PENDING' — bundle was built before final-verdict was updated.
BUNDLE_VALIDATION: FAIL
```

**Root cause:** R47 bundle was built when `final-verdict.md` still contained
`BUNDLE_VALIDATION: PENDING`. The final-verdict.md was then updated on disk (to PASS)
and committed in a second commit. But the bundle was NOT rebuilt after the update.
The bundle therefore froze the stale PENDING version.

**Current disk state:** `reports/r47/final-verdict.md` line 119 = `BUNDLE_VALIDATION: PASS`
**Bundled copy:** `repo/reports/r47/final-verdict.md` still contains `BUNDLE_VALIDATION: PENDING`

**R47 correct status:** `R47_ARTIFACT_PROOF_REAL_BUT_CLOSEOUT_ORDER_DEFECT_REMAINS`

---

## FODS Writer Schema Mismatch — Confirmed

**Writer reads:** `cell.get("value_type", "string")`
**R47 hardening tests pass:** `{"type": "float", "value": 3.14}` (using `"type"`, not `"value_type"`)
**Effect:** Float cells with `"type": "float"` fall through to string branch — typed values NOT preserved
**Parser outputs:** `value_type` field (canonical)
**Fix required:** Writer should accept both `"type"` (legacy alias) and `"value_type"` (canonical)

---

## Phase Audit 2 Scope Gap — Confirmed + Resolvable

**R47 Phase Audit 2 covered:** 12 formats
**sample/by-format/ contains:** 20 directories

**Missing formats:** ABW, CSV, FODG, FODP, Gnumeric, PAM, TSV, XPM
**Status of missing formats:** ALL 8 have `_provenance.yaml` files (project-owned-synthetic)
**Resolution:** Add audit entries for all 8 — no gap blocking completion

---

## State Linter Findings

| Finding | Level | Resolution |
|---------|-------|------------|
| r27-ai-platform-full-cycle.yaml: min_metadata_count=10 < 30 | WARNING | Classify as legacy contract (pre-floor-30 era) |
| r32-truth-matrix-gate-quality-and-drift-recovery.yaml: min_metadata_count=5 < 30 | WARNING | Classify as legacy contract (pre-floor-30 era) |
| skill_hardcoding (3x INFO) | INFO | Acceptable — FODS/FODT are current product formats |

---

## Sample Directories (20 total)

| Format | Phase Audit 2 (R47) | _provenance.yaml | Status |
|--------|---------------------|------------------|--------|
| ABW | NOT COVERED | PRESENT | Add in R48 |
| CSV | NOT COVERED | PRESENT | Add in R48 |
| DIF | COVERED | PRESENT | PASS |
| FODG | NOT COVERED | PRESENT | Add in R48 |
| FODP | NOT COVERED | PRESENT | Add in R48 |
| FODS | COVERED (PARTIAL) | ABSENT | Create in R48 |
| FODT | COVERED (PARTIAL) | ABSENT | Create in R48 |
| Gnumeric | NOT COVERED | PRESENT | Add in R48 |
| ODS | COVERED | PRESENT | PASS |
| ODT | COVERED | PRESENT | PASS |
| PAM | NOT COVERED | PRESENT | Add in R48 |
| PBM | COVERED | PRESENT | PASS |
| PGM | COVERED | PRESENT | PASS |
| PPM | COVERED | PRESENT | PASS |
| QOI | COVERED | PRESENT | PASS |
| SYLK | COVERED | PRESENT | PASS |
| TSV | NOT COVERED | PRESENT | Add in R48 |
| XCF | COVERED | PRESENT | PASS |
| XPM | NOT COVERED | PRESENT | Add in R48 |
| ZST | COVERED | PRESENT | PASS |

---

## R48 Sprint Objectives

1. Correct R47 closeout-order defect (IV + corrected supersession)
2. Add closeout-order tooling to prevent recurrence
3. Fix FODS writer type/value_type schema mismatch
4. Complete Phase Audit 2 (all 20 sample directories)
5. Create FODS/FODT `_provenance.yaml`
6. Kickoff Phase Audit 3 (FODS/FODT pilot)
7. Classify R27/R32 state linter warnings
8. Build Python installed-wheel smoke from bundled artifacts
9. .NET consumer proof from bundled artifacts
10. Final bundle with correct closeout order (PENDING → build → validate → PASS → rebuild)
