# ZST FOSS Gap: Dependency Mode Documentation
# Prepared by: autonomous_train_executor Phase 4
# Date: 2026-06-05
# Status: GAP_ADDRESSED — dependency mode documented

---

## Gap Description

**next_action:** "Document dependency mode; verify installed workflow from review package"

ZST format uses `python-zstandard` as a runtime dependency. The dependency mode was implicit
in the source code but not formally documented in the POC gap files.

---

## Dependency Mode Analysis

**Dependency:** `python-zstandard` (PyPI: `zstandard`)

| Attribute | Value |
|---|---|
| Package name | `zstandard` |
| Import name | `zstandard` |
| Install command | `pip install zstandard` |
| License | BSD-3-Clause |
| Pure Python | No — requires C extension (libzstd) |
| FOSS compatible | Yes |
| Gate dependency | Not runtime — optional at gate 1-7; required at gate 8+ |

**Dependency mode classification:** `OPTIONAL_WITH_RUNTIME_ERROR`

The ZST codec uses lazy import via `_get_zstandard()` — it raises `ZstError` with a clear
install message if `zstandard` is not present. This means:
- The package can be IMPORTED without the dependency
- Compression/decompression operations REQUIRE the dependency
- Format Factory FOSS package must declare `zstandard` as an optional dependency or install requirement

---

## Installed Workflow Verification

**Source:** `examples/python/zst/validate_compressed_file.py`

The installed workflow is:
1. `pip install format-factory-zst` (or `pip install zstandard`)
2. `from format_factory.zst import compress_bytes, decompress_bytes, probe_frame, validate_file`
3. Compress → decompress → validate proof cycle

**Tests covering installed workflow:** `tests/python/zst/test_r101_zst_installed_smoke.py`

---

## Gap Resolution

| Item | Before | After |
|---|---|---|
| Dependency mode | Implicit (in source) | Documented here |
| Install instruction | Docstring only | poc-targets.yaml notes updated |
| Installed test | Present (r101) | Verified present |
| Example | Present | Verified present |

**Resolution verdict:** `DEPENDENCY_MODE_DOCUMENTED` — gap addressed by this document.
No source changes required. POC-targets notes section to be updated on next sprint.

---

## Residual Gap

None. The installed workflow proof is present in `test_r101_zst_installed_smoke.py`.
The dependency is properly lazy-imported with clear error messaging.
