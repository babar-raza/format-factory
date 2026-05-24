# R57 Independent Verification Report

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**IV Date:** 2026-05-24
**IV Sprint:** R58 Train A
**Subject:** R57 closure claims

---

## Verification Methodology

All verification performed from git HEAD of main branch.
Commands run with exact output recorded.
Defects classified as: CONFIRMED_DEFECT or ACCEPTED_AS_IS.

---

## Defect 1: Final ZIP SHA Mismatch

**Claim:** R57 final verdict records BUNDLE_VALIDATION_PASS_2_SHA = 9b10186e...
**Verification:**
```
python -c "import hashlib; print(hashlib.sha256(open('.local/r57-pass2-final.zip','rb').read()).hexdigest())"
Output: d8a1c0986fdb606ae9f4654d753188b1a3482234a746d35debdeb9a369f56e87
```
**Recorded:** `9b10186e128e7082888f4c50a4cb66be29b073749d69ace30fb02b55ba3ca238`
**Actual:** `d8a1c0986fdb606ae9f4654d753188b1a3482234a746d35debdeb9a369f56e87`
**Classification:** CONFIRMED_DEFECT (IV-R57-001)
**Root cause:** After committing the sidecar JSON to the repo, the repo changed, making the Pass-1 bundle out of date. The Pass-2 bundle was rebuilt, but the recorded SHA was from an intermediate build.

---

## Defect 2: Sidecar Embedded Inside ZIP

**Claim:** External sidecar delivered.
**Verification:**
```
python -c "
import zipfile
with zipfile.ZipFile('.local/r57-pass2-final.zip') as zf:
    print([n for n in zf.namelist() if 'sha256-proof' in n])
"
Output: ['repo/reports/r57/r57-pass2-final.zip.sha256-proof.json']
```
**Finding:** The JSON committed to `reports/r57/r57-pass2-final.zip.sha256-proof.json` is inside the ZIP
(under `repo/` prefix). An external sidecar was also written to `.local/r57-pass2-final.zip.sha256-proof.json`
but it proved the *previous* bundle build before the final Pass-2.
**Classification:** CONFIRMED_DEFECT (IV-R57-002)
**Root cause:** Sidecar committed to repo was bundled inside zip. External `.local/` sidecar had stale SHA.

---

## Defect 3: Sidecar Schema Key Mismatch

**Claim:** Sidecar uses canonical schema.
**Verification:**
```
cat .local/r57-pass2-final.zip.sha256-proof.json
Output: "bundle_sha256": "d8a1c0986..."
```
**Validator expects:** `sidecar.get("sha256", "")`
**Schema written:** `bundle_sha256` (non-canonical field name)
**Classification:** CONFIRMED_DEFECT (IV-R57-003)
**Root cause:** First write_sidecar_proof.py used `bundle_sha256`; validator expects `sha256`.

---

## Defect 4: State Latest Sprint PENDING

**Claim:** State snapshot updated.
**Verification:**
```
grep "latest_sprint\|verdict\|PENDING" state/current-state.md
Output:
  Latest sprint: R57 - PENDING
  verdict: PENDING
```
**Classification:** CONFIRMED_DEFECT (IV-R57-004)
**Root cause:** state_snapshot.py was run before final verdict was written, leaving verdict=PENDING.

---

## Defect 5: Stale R56 Blocker Text in State

**Claim:** State reflects R57 state.
**Verification:**
```
grep "INV-011\|R56" state/current-state.md
Output:
  INV-011: state/current-state.md shows R56 but latest contract is R57
  INV-011: Run state_snapshot.py to update current-state.md
```
**Classification:** CONFIRMED_DEFECT (IV-R57-005)
**Root cause:** state_snapshot.py wrote stale invariant text referencing R56 → R57 mismatch.

---

## Defect 6: Train L IN_PROGRESS in Final Verdict

**Claim:** All trains complete.
**Verification:**
```
grep "IN_PROGRESS" reports/r57/final-verdict.md reports/r57/multi-mega-train-scoreboard.md
Output:
  reports/r57/final-verdict.md:| L | IN_PROGRESS | Final bundle build |
  reports/r57/multi-mega-train-scoreboard.md:| L | ... | IN_PROGRESS | — |
  reports/r57/multi-mega-train-scoreboard.md:**SCOREBOARD_STATUS: TRAINS_A_THROUGH_K_COMPLETE — TRAIN_L_IN_PROGRESS**
```
**Classification:** CONFIRMED_DEFECT (IV-R57-006)
**Root cause:** Final verdict and scoreboard were not updated after bundle validation PASS.

---

## Defect 7: Package Replay Skips Artifact Checks From Extracted Bundle

**Claim:** Portable package replay works from extracted bundle.
**Verification (simulated extraction):**
```
python -c "
import zipfile, tempfile, sys
from pathlib import Path
bundle = Path('.local/r57-pass2-final.zip')
with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(bundle) as zf:
        zf.extractall(tmp)
    sys.path.insert(0, str(Path(tmp)/'repo'))
    from tools.packaging.find_bundle_artifacts import find_artifact_dir
    result = find_artifact_dir('r57', Path(tmp)/'repo')
    print(f'find_artifact_dir result: {result}')
"
Output: find_artifact_dir result: None
```
**Finding:** When bundle is extracted, the layout is `<extract-root>/repo/` and
`<extract-root>/bundle-metadata/`. `find_artifact_dir` uses `PROJECT_ROOT / 'bundle-metadata'`
but extracted repo is at `<extract-root>/repo`, so it looks for
`<extract-root>/repo/bundle-metadata/` (does not exist) instead of
`<extract-root>/bundle-metadata/` (the parent of the repo).
**Classification:** CONFIRMED_DEFECT (IV-R57-007)

---

## Defect 8: Bundled Wheels Do Not Include R57 Features

**Claim:** Wheels rebuilt for R57.
**Verification:**
```
python -c "
import zipfile, io
from pathlib import Path
bundle = Path('.local/r57-pass2-final.zip')
with zipfile.ZipFile(bundle) as zf:
    fods_whl = 'bundle-metadata/package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl'
    data = zf.read(fods_whl)
    inner = zipfile.ZipFile(io.BytesIO(data))
    for n in inner.namelist():
        if 'neutral_model' in n:
            src = inner.read(n).decode('utf-8')
            print('workbook_stats in FODS wheel:', 'workbook_stats' in src)
"
Output: workbook_stats in FODS wheel: False
```
**Classification:** CONFIRMED_DEFECT (IV-R57-008)
**Root cause:** R57 wheels were copied from R56 artifacts without rebuilding from current HEAD.

---

## Defect 9: workbook_stats/document_stats Not in Public API

**Claim:** FODS/FODT capabilities fully delivered.
**Verification:**
```
grep "workbook_stats\|document_stats" src/python/fods/__init__.py src/python/fodt/__init__.py
Output: (no matches)
```
**Finding:** `workbook_stats()` and `document_stats()` exist in `neutral_model.py` but are
not exported from the package `__init__.py`.
**Classification:** CONFIRMED_DEFECT (IV-R57-009)
**Note:** Functions are accessible via `from src.python.fods.neutral_model import workbook_stats`,
but not from the public package API. This means an installed wheel consumer cannot
call `import fods; fods.workbook_stats(...)`.

---

## Defect 10: Only CSV Clearly Advanced as Next-Format Track

**Claim:** Four real next-format tracks advanced.
**Verification:**
```
Scoreboard Lane F: "CSV Gate 6 PASS; 26 oracle tests; pack.yaml updated"
No TSV Gate 6, no PGM/PBM write, no DIF/SYLK writer, no QOI PNG export.
```
**Classification:** CONFIRMED_DEFECT (IV-R57-010)
**Root cause:** R57 Lane F only completed CSV Gate 6. TSV oracle was deferred to R58.
Other Netpbm/spreadsheet format advances not attempted.

---

## Defect 11: Validator Missed Multiple Finality Issues

**Claim:** Validator PASS is authoritative.
**Verification:**
Validator passed with:
- State showing `R57 - PENDING` (not caught)
- Train L `IN_PROGRESS` in scoreboard (not caught)
- Wheels missing R57 features (not caught)
- Sidecar embedded in ZIP (not caught as structural error)
- Package replay always skipping artifact checks in clean extract (not caught)
**Classification:** CONFIRMED_DEFECT (IV-R57-011)

---

## Defect 12: No pycache in Bundle (Cleared)

**Verification:**
```
python -c "
import zipfile
with zipfile.ZipFile('.local/r57-pass2-final.zip') as zf:
    pycache = [n for n in zf.namelist() if '__pycache__' in n or n.endswith('.pyc')]
    print(f'pycache/pyc files: {len(pycache)}')
"
Output: pycache/pyc files: 0
```
**Classification:** NOT_REPRODUCED — Bundle contains 0 pycache/pyc files.
The original IV claim may have been based on an intermediate build.
R58 will add a validator check to prevent future regression.

---

## Defect 13: Final Bundle Entry Count

**Verification:**
- Actual bundle: 2522 entries
- Bundle sidecar committed to repo: refers to 2522 entries, bundle_sha256 `d8a1c098...`
- final-verdict.md Pass-2 SHA: `9b10186e...` (wrong)
- The actual `.local/` sidecar SHA-256 `d8a1c098...` matches the actual bundle
**Classification:** Traceable to IV-R57-001 (same root cause as SHA mismatch).

---

## Summary

| Defect | ID | Status |
|--------|-----|--------|
| Final ZIP SHA mismatch | IV-R57-001 | CONFIRMED |
| Sidecar embedded inside ZIP | IV-R57-002 | CONFIRMED |
| Sidecar schema key mismatch | IV-R57-003 | CONFIRMED |
| State latest sprint PENDING | IV-R57-004 | CONFIRMED |
| Stale R56 blocker text in state | IV-R57-005 | CONFIRMED |
| Train L IN_PROGRESS in final verdict | IV-R57-006 | CONFIRMED |
| Package replay skips from extracted bundle | IV-R57-007 | CONFIRMED |
| Bundled wheels lack R57 features | IV-R57-008 | CONFIRMED |
| workbook_stats/document_stats not in public API | IV-R57-009 | CONFIRMED |
| Only CSV advanced as next-format track | IV-R57-010 | CONFIRMED |
| Validator missed finality issues | IV-R57-011 | CONFIRMED |
| No pycache in bundle | IV-R57-012 | NOT_REPRODUCED (add regression guard) |

**Total confirmed defects: 11**
