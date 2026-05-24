# Package Artifact Manifest / Hash Enforcement — R57 Train D

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Train:** D — Package Artifact Manifest/Hash Enforcement
**Date:** 2026-05-23
**Closes:** IV-R56-006, IV-R56-007

---

## 1. Root Cause

`package-artifact-manifest.yaml` was written with truncated 32-char hex values for
`wheel_sha256`. Inspection reveals these are the first 32 chars of the actual SHA-256
(not a different algorithm). The manifest was produced with Python's `hashlib.sha256`
but the output was sliced to 32 chars (likely `sha.hexdigest()[:32]`).

The validator's `check_artifact_inventory()` regex `[0-9a-fA-F]{64}` required exactly
64 chars, so the truncated values were silently skipped — no validation occurred.

---

## 2. Manifest Fix (IV-R56-006)

Recomputed all 7 wheel SHA-256 values from actual `.whl` bytes using:
```python
hashlib.sha256(whl.read_bytes()).hexdigest()
```

**Updated `.local/r56-metadata/package-artifact-manifest.yaml`:**

| Package | Old (32 chars) | New (64 chars) |
|---------|---------------|---------------|
| fods | 9c10377a...9ff | 9c10377a...e491 |
| fodt | 73be7767...b85 | 73be7767...00ba |
| zst | 328561e7...e12 | 328561e7...c8e0 |
| fodp | fdebe858...a7 | fdebe858...c65 |
| fodg | b3d4173a...1f | b3d4173a...3f8 |
| gnumeric | ed079be8...0eb | ed079be8...fd5 |
| abw | 6cf0c5d9...5d | 6cf0c5d9...d6a |

Note: The truncated values were the first 32 chars of the correct SHA-256 — the algorithm
was correct but the output was sliced. Confirmed by: truncated value matches sha256[:32].

---

## 3. Validator Fix (IV-R56-007)

Added truncated-SHA detection in `check_artifact_inventory()`:
- Scans every `sha256:` / `SHA-256:` / `wheel_sha256:` line
- Matches hex values of 16-63 chars (too short for SHA-256)
- Emits `ARTIFACT_SHA_TRUNCATED` error with value, length, and fix instruction

This catches the exact R56 defect pattern and prevents future regressions.

---

## 4. Test Evidence

After manifest update, all 56 Train B/C/D tests pass:
- `test_r57_package_rc.py::TestPackageManifest::test_manifest_sha256_values_are_64_chars` — PASS
- `test_r57_pending_marker_strictness.py` — 8/8 PASS
- `test_r57_sidecar_required_top_level.py` — 11/11 PASS
- `test_r57_final_proof_completeness.py` — 11/11 PASS
- `test_r57_package_rc.py` — 26/26 PASS

**Combined: 56/56 PASS**

---

**STATUS: TRAIN_D_COMPLETE — manifest updated with full 64-char SHA-256; validator hardened; 56 tests PASS**
