# R58 Extracted Package Replay Repair

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Train:** D
**Date:** 2026-05-24

---

## Problem Repaired

IV-R57-007: `find_artifact_dir` did not check `PROJECT_ROOT.parent/bundle-metadata/package-artifacts`.

When a bundle is extracted, the layout is:
```
<extract-root>/
  repo/         <- project_root when running tests
  bundle-metadata/
    package-artifacts/
      *.whl files
```

The old `find_artifact_dir` checked `project_root/bundle-metadata/` (which doesn't exist in extracted layout)
but not `project_root.parent/bundle-metadata/` (which does exist).

---

## Fix Applied

`tools/packaging/find_bundle_artifacts.py` candidates list now includes:
```python
root.parent / "bundle-metadata" / "package-artifacts",  # R58 IV-R57-007
```

Same fix applied to `find_manifest_path`.

Priority order:
1. `.local/<run>-metadata/package-artifacts/`  (local dev)
2. `project_root/bundle-metadata/package-artifacts/`  (unusual layout)
3. `project_root.parent/bundle-metadata/package-artifacts/`  (standard extracted bundle layout)
4. `project_root/reports/<run>/package-artifacts/`  (legacy)

---

## Verification

```
pytest tests/packaging/test_r58_extracted_bundle_replay.py -v
```
Result: **6/6 PASS**

Including `test_r57_bundle_extraction_finds_artifacts`:
- Extracts actual R57 pass-2 bundle to temp dir
- Verifies `find_artifact_dir("r57", extracted_repo)` returns the parent-dir artifacts
- No manual symlink required

---

## Tests Added

- tests/packaging/test_r58_extracted_bundle_replay.py (6 tests, all PASS)
