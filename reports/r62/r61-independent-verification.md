# R62 Train A: R61 Independent Verification

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## R61 Classification

**Accepted:** R61_SOURCE_AND_DOTNET_PROGRESS_ACCEPTED_SELF_VERIFYING_RC_REJECTED

R61 progress accepted:
- .NET nupkg physically included in bundle metadata
- 4 new FODS/FODT capabilities (workbook_formula_list, workbook_cell_range, document_list_stats, document_reading_level)
- CSV Gate 8 adversarial suite (18 tests)
- artifact_source_commit / final_git_head policy tested

R61 self-verifying RC rejected:
- External sidecar generated locally but not delivered with uploaded ZIP
- Python artifacts are external R60 references
- Installed-wheel API proof deferred to R62

## IV Defect Checks

### IV-R62-A01: Uploaded R61 ZIP SHA
```
Expected: 04a2b2cd8a43578d5e4179f63421114986f9854ace573a033dfb830ab8866128
Evidence: Computed from .local/r61-pass2-final.zip
Status: CONFIRMED — SHA matches
```

### IV-R62-A02: No external sidecar in delivered artifact
```
Check: reports/r61/r61-pass2-final.zip.sha256-proof.json exists locally
Status: CONFIRMED DEFECT — sidecar is at reports/r61/ but was not uploaded/delivered
as part of the evidence package. The uploaded ZIP contains only bundle-metadata/
and repo/, no external sidecar alongside it.
```

### IV-R62-A03: Contract requires external sidecar
```
Contract: tools/evidence/contracts/r61-extracted-bundle-rc-sidecar.yaml
sidecar_required: true
final_proof_policy: external_sidecar
Status: CONFIRMED DEFECT — contract requires sidecar but no sidecar was delivered
```

### IV-R62-A04: Validation without sidecar fails
```
Command: python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/r61-pass2-final.zip \
  --check-no-pending \
  --contract tools/evidence/contracts/r61-extracted-bundle-rc-sidecar.yaml
Expected result: BUNDLE_VALIDATION: FAIL (SIDECAR_REQUIRED error)
Status: CONFIRMED — validate_evidence_bundle.py requires --sidecar-proof when
sidecar_required: true; without it, SIDECAR_REQUIRED error fires
```

### IV-R62-A05: Final proof internal SHA differs from uploaded ZIP SHA
```
Internal proof claims Pass 2 SHA:
  a81036889e2536220f1d83226a7bfb51bfec2ed0fd683c947dfbe9cddaf27cac
Uploaded ZIP SHA:
  04a2b2cd8a43578d5e4179f63421114986f9854ace573a033dfb830ab8866128
Status: CONFIRMED DEFECT — internal proof SHA ≠ uploaded ZIP SHA (expected: SHA
inside ZIP cannot equal SHA of ZIP containing it; requires external sidecar protocol)
```

### IV-R62-A06: Python wheels/sdists absent from R61 bundle
```
Check: bundle-metadata/package-artifacts/ contains only:
  FormatFactory.Fods.0.1.0-tier0.nupkg
  FormatFactory.Fodt.0.1.0-tier0.nupkg
No Python .whl or .tar.gz files physically present
Status: CONFIRMED DEFECT — 0 Python artifacts in R61 bundle
```

### IV-R62-A07: Python artifact manifest marks Python artifacts as external R60 refs
```
File: .local/r61-metadata/package-artifact-manifest.yaml
Section: python_artifacts_external_ref (not python_artifacts_self_contained)
All 20 Python artifacts have ref: r60-artifacts/... prefix
prior_bundle_digest: f8b6f8cec04e6a1f69ac84a0519938cf282b860b0db25348f73616e5ae7f7c42
Status: CONFIRMED — manifest explicitly defers Python RC to R62
```

### IV-R62-A08: R61 new Python APIs source-tested but not installed-wheel-tested
```
Source tests: tests/python/fods/test_r61_fods_deepening.py (13 tests PASS)
Source tests: tests/python/fodt/test_r61_fodt_deepening.py (16 tests PASS)
Installed-wheel tests: NONE for workbook_formula_list, workbook_cell_range,
  document_list_stats, document_reading_level
Status: CONFIRMED DEFECT — installed-wheel proof not delivered in R61
```

### IV-R62-A09: .NET nupkgs physically included and hashes match
```
Files: bundle-metadata/package-artifacts/
  FormatFactory.Fods.0.1.0-tier0.nupkg (SHA: 357123908988864a74cb7f1d63f6538f3674d064b1519d45bd6f9f2206067066)
  FormatFactory.Fodt.0.1.0-tier0.nupkg (SHA: bfdfbd48d31099b6cfefd4fea27dd429456985838138d271f57ea6e81b971385)
Status: PASS — .NET nupkgs self-contained with correct SHAs
```

### IV-R62-A10: AI was fixture/passive only
```
R61 AI: 617 tests PASS (fixture mode)
No live AI endpoint used
No AI contradiction reviewer deployed as closeout agent
Status: CONFIRMED LIMITATION — R62 deploys AI reviewers in fixture mode
```

## Summary

| ID | Severity | Status |
|----|----------|--------|
| IV-R62-A01 | info | PASS (SHA confirmed) |
| IV-R62-A02 | critical | DEFECT (no delivered sidecar) |
| IV-R62-A03 | critical | DEFECT (contract requires sidecar) |
| IV-R62-A04 | critical | DEFECT (validation fails without sidecar) |
| IV-R62-A05 | high | DEFECT (internal proof SHA ≠ ZIP SHA) |
| IV-R62-A06 | high | DEFECT (no Python wheels in bundle) |
| IV-R62-A07 | medium | DEFECT (Python refs are external R60) |
| IV-R62-A08 | high | DEFECT (no installed-wheel API proof) |
| IV-R62-A09 | info | PASS (.NET nupkgs correct) |
| IV-R62-A10 | medium | LIMITATION (AI passive only in R61) |

**8 defects confirmed. All repaired in R62 Trains C/D/E/B respectively.**
