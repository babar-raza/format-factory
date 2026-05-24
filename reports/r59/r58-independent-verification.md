# R59 Train A — R58 Independent Verification

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## IV Methodology

Independent verification of R58 evidence bundle `.local/r58-pass2-final.zip` and all
R58 reports. Each item verified by command or file inspection.

---

## IV-R58-001 — Uploaded ZIP SHA matches external sidecar

**Verification:**
```
Actual SHA-256: d040a288d6be1399196380a02e9870527d7b204e091f16642ec89abbcc5d9cb5
Sidecar SHA:    d040a288d6be1399196380a02e9870527d7b204e091f16642ec89abbcc5d9cb5
Match: True
```
**Result: CONFIRMED_PASS** — Sidecar SHA matches actual bundle.

---

## IV-R58-002 — Validator fails without sidecar, passes with sidecar

**Verification:** Ran validator without `--sidecar-proof`:
- SIDECAR_REQUIRED error fires (expected FAIL)
Ran validator with `--sidecar-proof`:
- BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS

**Result: CONFIRMED_PASS** — Sidecar enforcement is fail-closed.

---

## IV-R58-003 — R58 final-verdict.md still marks Train M as IN_PROGRESS

**Verification:** `reports/r58/final-verdict.md` line 37:
```
| M | IN_PROGRESS | Final adversarial IV + evidence bundle |
```
Train M was NEVER marked COMPLETE in the final-verdict. The scoreboard shows ALL_COMPLETE,
but the final-verdict itself says IN_PROGRESS. This is a direct contradiction.

**Result: CONFIRMED_DEFECT** → IV-R58-003

---

## IV-R58-004 — R58 scoreboard says Train M complete

**Verification:** `reports/r58/multi-mega-train-scoreboard.md`:
```
| M | Final adversarial IV + bundle | COMPLETE | ...
**SCOREBOARD_STATUS: ALL_COMPLETE**
```
Scoreboard says complete, final-verdict says IN_PROGRESS.

**Result: CONFIRMED_DEFECT** → IV-R58-004 (Scoreboard/verdict contradiction)

---

## IV-R58-005 — Validator passed despite current-run final-verdict IN_PROGRESS

**Verification:** Ran final validation of R58 bundle. Result was BUNDLE_VALIDATION: PASS.
The `check_scoreboard_lanes_in_progress` function should have caught "IN_PROGRESS" in
`repo/reports/r58/final-verdict.md` — but it did not.

**Result: CONFIRMED_DEFECT** → IV-R58-005

---

## IV-R58-006 — Root cause: final-verdict scanner overwrites current-run verdict

**Verification:** Python inspection of zip namelist:
```python
last_verdict = [e for e in zf.namelist()
                if e.endswith('/final-verdict.md') and e.startswith('repo/reports/')][-1]
# = 'repo/reports/skills-system-hardening/20260517/final-verdict.md'
```

`check_scoreboard_lanes_in_progress` loops over ALL entries and overwrites `verdict_content`
for every `final-verdict.md` found. The LAST one alphabetically is:
`repo/reports/skills-system-hardening/20260517/final-verdict.md`

This file (from the skills PRD hardening sprint) does NOT contain "IN_PROGRESS", so the
check passes silently even though `repo/reports/r58/final-verdict.md` has IN_PROGRESS.

Root cause: no `run_number` guard; arbitrary historical final-verdicts can override the
current-run final-verdict content.

**Result: CONFIRMED_DEFECT** → IV-R58-006 (root cause of IV-R58-005)

---

## IV-R58-007 — Internal proof SHA stale

**Verification:** `bundle-metadata/final-bundle-validation-proof.txt`:
```
SHA-256: 676451bf69e093d68ad36512224218e4a0d906de92e5fca340960bcbec224310
```
Actual uploaded bundle SHA (from sidecar):
```
SHA-256: d040a288d6be1399196380a02e9870527d7b204e091f16642ec89abbcc5d9cb5
```
Mismatch. The proof file contains SHA from a prior build (before final commit).

**Result: CONFIRMED_DEFECT** → IV-R58-007

---

## IV-R58-008 — test_r58_extracted_bundle_replay.py: 4/6 pass, 2 real extraction tests skip

**Verification:** `test_r58_extracted_bundle_replay.py`:
- `test_r57_bundle_extraction_finds_artifacts` → SKIP (requires `.local/r57-pass2-final.zip`)
- `test_extracted_bundle_manifest_found` → SKIP (same reason)
- 4 layout tests pass using tmp_path fixtures

The tests do not prove that the CURRENT bundle (R58) extraction finds artifacts.
Tests skip the real extraction check unless `.local/r57-pass2-final.zip` is present.

**Result: CONFIRMED_DEFECT** → IV-R58-008

---

## IV-R58-009 — Full packaging suite fails from extracted bundle

**Verification:** Legacy packaging tests hardcode:
- `.local/r55-metadata/package-artifacts/`
- `.local/r56-metadata/package-artifacts/`
- `.local/r57-metadata/package-artifacts/`

From extracted bundle, none of these paths exist. Tests fail with path-not-found.
This means full packaging suite is NOT replayable from extracted bundle.

**Result: CONFIRMED_DEFECT** → IV-R58-009

---

## IV-R58-010 — Wheels present, sdists absent

**Verification:** `.local/r58-metadata/package-artifacts/`:
```
7 .whl files, 0 .tar.gz files
```
No source distributions built. Python RC claim requires wheel + sdist per R59 hard prohibition.

**Result: CONFIRMED_DEFECT** → IV-R58-010

---

## IV-R58-011 — .nupkg files not in package-artifact-manifest.yaml

**Verification:** `.local/r58-metadata/package-artifact-manifest.yaml` lists only wheels;
`.local/r58-metadata/dotnet-nupkgs/` has 2 .nupkg files. No nupkg section in manifest.

**Result: CONFIRMED_DEFECT** → IV-R58-011

---

## IV-R58-012 — .NET raw logs and local consumer proof absent

**Verification:** `reports/r58/dotnet-nuget-local-proof.md` contains only summary counts
(302/302 PASS, pack results). No raw bounded dotnet test logs, no local consumer project
restore/install proof documented.

**Result: CONFIRMED_DEFECT** → IV-R58-012

---

## IV-R58-013 — No pycache/nested ZIP/embedded sidecar defect

**Verification:**
- pycache: no `__pycache__` or `.pyc` in bundle repo/ section
- Nested ZIPs: none in repo/ section
- Embedded sidecar: sidecar not committed, not in bundle

**Result: CONFIRMED_PASS** — No hygiene defect.

---

## IV-R58-014 — Four-track next-format advancement credible and scoped

**Verification:**
- TSV Gate 6: 21 oracle tests in `tests/python/tsv/test_r58_tsv_gate6_oracle.py` — ALL PASS
- PGM deepening: 17 tests — ALL PASS
- PBM deepening: 18 tests — ALL PASS
- DIF deepening: 20 tests — ALL PASS
- `acquisition-packs/tsv/pack.yaml` gate_6 section added

Scope correct: TSV G6 + PGM/PBM/DIF depth tests. No overclaim.

**Result: CONFIRMED_PASS** — Four-track advancement real and credible.

---

## IV Summary

| IV ID | Finding | Status |
|-------|---------|--------|
| IV-R58-001 | Sidecar SHA matches bundle | PASS |
| IV-R58-002 | Sidecar enforcement fail-closed | PASS |
| IV-R58-003 | Train M IN_PROGRESS in final-verdict | DEFECT |
| IV-R58-004 | Scoreboard/final-verdict contradiction | DEFECT |
| IV-R58-005 | Validator passed despite IN_PROGRESS | DEFECT |
| IV-R58-006 | Root cause: skills-hardening verdict overwrites r58 | DEFECT |
| IV-R58-007 | Stale internal proof SHA | DEFECT |
| IV-R58-008 | Extraction tests skip real bundle checks | DEFECT |
| IV-R58-009 | Full packaging suite fails from extracted bundle | DEFECT |
| IV-R58-010 | No sdists in artifacts | DEFECT |
| IV-R58-011 | .nupkg not in manifest | DEFECT |
| IV-R58-012 | .NET raw logs/consumer proof absent | DEFECT |
| IV-R58-013 | No pycache/nested ZIP/embedded sidecar | PASS |
| IV-R58-014 | Four-track advancement credible | PASS |

**DEFECTS: 10 | PASSES: 4**

## TRAIN_A_COMPLETE
