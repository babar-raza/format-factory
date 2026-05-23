# Package RC Self-Contained Artifact Train — Train D Report

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Train:** D — Package RC Self-Contained
**Date:** 2026-05-23
**Corrects:** IV-R55-002 (package manifest claimed `none` while verdict said "7 packages built")

---

## 1. R55 Defect Corrected

**IV-R55-002:** R55 `package-artifact-manifest.yaml` declared `r55_installed_artifact_policy: none`,
but `phase-audit-6-summary.txt` and `final-verdict.md` claimed "7 packages built". This contradiction
is the root cause.

**R56 resolution:** All 7 wheels physically rebuilt from R56 source, placed in
`.local/r56-metadata/package-artifacts/`, and manifest now declares `r56_installed_artifact_policy: self_contained`.

---

## 2. Package Build Results

**Build tool:** `packaging/python/build-local-packages.py`
**Python version:** 3.13
**Build date:** 2026-05-23

| Package | Wheel | Size (bytes) | Status |
|---------|-------|-------------|--------|
| aspose-format-factory-fods | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 15,654 | BUILT |
| aspose-format-factory-fodt | aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 18,039 | BUILT |
| aspose-format-factory-zst | aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | 9,780 | BUILT |
| aspose-format-factory-fodp | aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl | 8,851 | BUILT |
| aspose-format-factory-fodg | aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl | 8,970 | BUILT |
| aspose-format-factory-gnumeric | aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl | 8,707 | BUILT |
| aspose-format-factory-abw | aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl | 8,410 | BUILT |

**Build summary:** 7/7 built, 0 errors.

Note: FODT wheel (18,039 bytes) is larger than FODS (15,654 bytes) because it now includes the
R56 hyperlink and nested list implementation (writer.py ~307 lines vs ~200 lines).

---

## 3. Installed Smoke Tests

Ran from fresh venv (`.local/r56-venv-smoke`) with no sys.path manipulation:

```
FODS_PARSE: PASS
FODT_HYPERLINK_ROUND_TRIP: PASS
ALL_INSTALLED_SMOKE: PASS
```

**FODS smoke:** parse minimal .fods XML → `doc['sheets'][0]['rows'][0]['cells'][0]['value'] == 'Hello'`
**FODT smoke:** parse .fodt with `text:a xlink:href` → `_collect_runs()` captures href → `document_to_xml()` round-trips URL and link text

---

## 4. Wheel Content Verification

FODT wheel R56 source confirmed by content inspection:
- `writer.py` present in wheel ✓
- `xlink` namespace in writer.py ✓ (R56 hyperlink code)
- `level_stack` algorithm in writer.py ✓ (R56 nested list code)

---

## 5. Package Artifact Manifest

**Path:** `.local/r56-metadata/package-artifact-manifest.yaml`
**Policy:** `r56_installed_artifact_policy: self_contained`
**Smoke result:** `FODS_PARSE_PASS_AND_FODT_HYPERLINK_ROUND_TRIP_PASS`
**publication_authorized:** false

---

## 6. Test Evidence

**New test file:** `tests/packaging/test_r56_package_rc.py`
**Result:** 23/23 PASS

Classes:
- `TestPackageArtifactsExist` (16 tests): all 7 wheels exist and are non-zero
- `TestWheelContents` (4 tests): FODT writer has xlink and level_stack; FODS writer present
- `TestPackageManifest` (3 tests): manifest exists, self_contained policy, PASS smoke recorded

---

## 7. Governance

- `publication_authorized: false` in all manifests and build scripts
- No PyPI upload performed
- Wheels in `.local/` (gitignored)

---

**STATUS: TRAIN_D_COMPLETE**
