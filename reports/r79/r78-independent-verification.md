# R79 Train A — R78 Independent Verification

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** A

## SHA Chain Verification

| Artifact | Claimed SHA | Supervisor SHA | Result |
|---|---|---|---|
| Supervisor review package | a0f23a141ec412fa8f6b01358906b1117fc847fb8be5dbada7651fd6922636b4 | a0f23a141ec412fa (supervisor) | MATCH |
| Delivery package | 1bd82528c648e822040f267d26f9a58a70ce23fcdfa3eccbb57a9b5876698526 | 1bd82528c648e822 (supervisor) | MATCH |
| Inner evidence ZIP | 46890c1aac67dc2bc4736d1a44c269d5c79da3f74b25b8d086c3346e199e33d3 | 46890c1aac67dc2b (supervisor) | MATCH |
| Sidecar file | 5764af3e6dc39026183bfd4b9f719fb3bfd132df4f39c0dfa24eb5fd537ef18c | 5764af3e6dc39026 (supervisor) | MATCH |

SHA_CHAIN_VERIFICATION: PASS

## Bundle Validation (Supervisor-Reproduced)

- BUNDLE_VALIDATION: PASS
- SIDECAR_PROOF_VALIDATION: PASS

## Package Artifact Verification

### R78 FODS Wheel Check (from R78 installed package)

The FODS wheel in the R78 package was built from PRE-R77 source. Evidence:

| API | Exists in src/python/fods/__init__.py | In R78 installed wheel |
|---|---|---|
| workbook_add_sheet | YES | NO — MISSING |
| workbook_rename_sheet | YES | NO — MISSING |
| workbook_remove_sheet | YES | NO — MISSING |
| workbook_set_cell_value | YES | Probably present |
| parse_fods | YES | YES |

FODS_WHEEL_STALE: CONFIRMED (R77 sheet management APIs absent)

### R78 FODT Wheel Check

| API | Exists in src/python/fodt/__init__.py | In R78 installed wheel |
|---|---|---|
| document_append_paragraph | YES | NO — MISSING |
| document_remove_paragraph | YES | NO — MISSING |
| document_paragraph_count | YES | NO — MISSING |
| parse_fodt | YES | YES |

FODT_WHEEL_STALE: CONFIRMED (R77 paragraph management APIs absent)

### Module Version Mismatch

- `fods.__version__` (from source PACKAGE_VERSION in constants.py): `"0.1.0"`
- Wheel metadata version: `"0.1.0.dev0"`
- STATUS: MISMATCH — D78-04 CONFIRMED

### SDist Old Nested Artifacts

The build dir `.local/package-builds/python-foss/aspose-format-factory-fods/` contains
directories: dist/, dist-r43/, dist-r44/, dist-r45/, dist-r46/, dist-r47/ from prior builds.
Since `pyproject.template.toml` has no sdist exclude for dist/ directories, the sdist
packages the entire build dir including these old artifacts.

SDIST_OLD_ARTIFACTS: CONFIRMED — D78-05

### Package Install Smoke Used Repo Imports

`bundle-metadata/installed-public-api-smoke-summary.txt` (from R78) uses:
```
from src.python.fods import ...
from src.python.fodt import ...
```
This tests REPO source, not installed package. Invalid for product readiness proof.

REPO_IMPORT_SMOKE: CONFIRMED — D78-06

### Reproducibility Proof Uses Wrong Import

`reports/r78/fods-reproducibility-proof.md` used:
```python
from aspose_format_factory_fods import parse_fods
```
The installed module is `import fods`, not `import aspose_format_factory_fods`.
This import FAILS after installing the actual wheel.

WRONG_IMPORT_NAMESPACE: CONFIRMED — D78-07

### Final IV Wording Issues

`bundle-metadata/final-independent-verification.txt` contains:
- `CLAIMS_VERIFIED: 14/15` — not a clean 15/15
- `BUNDLE_VALIDATION_PASS_1_SHA: unfilled` — unfilled marker
- `1 pending: state/current-state.md update after bundle build`

STALE_IV_WORDING: CONFIRMED — D78-08

### Stale R77 Naming

`bundle-metadata/supervisor-review-package-validation-summary.txt` references R77 filenames
and R77 artifact names — copied from R77 template.

STALE_R77_NAMES: CONFIRMED — D78-09

### Stale Placeholder Scan

`bundle-metadata/placeholder-scan-summary.txt` scans `reports/r77/final-verdict.md`
and R76 report files — not R78/R79 current sprint files.

STALE_PLACEHOLDER_SCAN: CONFIRMED — D78-10

### State INV-011 in Production Blockers

`state/current-state.md` production blockers include:
```
INV-011: state/current-state.md shows R77 but latest contract is R78
INV-011: Run state_snapshot.py to update current-state.md
```
These are stale from the R78 build time — state_snapshot.py was run during the R78
sprint before the R78 evidence contract was the latest.

STALE_INV_011: CONFIRMED — D78-11 (will be fixed at end of R79)

### ZST No-Network Install

The `zstandard` dependency wheel is not included in the R78 review package.
Installing ZST with `--no-index --find-links package-artifacts/` fails because
`zstandard` is not found.

ZST_OFFLINE_REPLAY_FAILS: CONFIRMED — D78-12

### FODT Structural Gap

`document_append_paragraph`, `document_remove_paragraph`, `document_paragraph_count`
write to `doc["body"]["blocks"]`. The writer `write_fodt` reads from `doc["blocks"]`
(root level). These are separate sections; appended paragraphs are NOT serialized.

FODT_STRUCTURAL_GAP: CONFIRMED — GAP-FODT-STRUCT-001 / D78-13

### .NET No Test Projects

No `.csproj` test project files found in `src/net/fods/` or `src/net/fodt/`.
The .NET implementation is an untested prototype.

DOTNET_UNTESTED: CONFIRMED — D78-14

## Defect Classification Summary

| ID | Classification |
|---|---|
| D78-01 | CONFIRMED_CARRIED_TO_R79 (root: stale wheel build) |
| D78-02 | CONFIRMED_CARRIED_TO_R79 |
| D78-03 | CONFIRMED_CARRIED_TO_R79 |
| D78-04 | CONFIRMED_CARRIED_TO_R79 |
| D78-05 | CONFIRMED_CARRIED_TO_R79 |
| D78-06 | CONFIRMED_CARRIED_TO_R79 |
| D78-07 | CONFIRMED_CARRIED_TO_R79 |
| D78-08 | CONFIRMED_CARRIED_TO_R79 |
| D78-09 | CONFIRMED_CARRIED_TO_R79 |
| D78-10 | CONFIRMED_CARRIED_TO_R79 |
| D78-11 | CONFIRMED_CARRIED_TO_R79 |
| D78-12 | CONFIRMED_CARRIED_TO_R79 |
| D78-13 | CONFIRMED_CARRIED_TO_R79 |
| D78-14 | CONFIRMED_CARRIED_TO_R79 |
| D78-15 | CONFIRMED_CARRIED_TO_R79 |
| D78-16 | CONFIRMED_CARRIED_TO_R79 |
| D78-17 | CONFIRMED_CARRIED_TO_R79 |

TOTAL_DEFECTS_CARRIED: 17/17
R78_IV_RESULT: ALL_17_SUPERVISOR_FINDINGS_CONFIRMED
