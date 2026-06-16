# ZST — Gate 11 Commercial Readiness Packet
# Prepared by: Agent (agent-owned preparation — submission requires human authorization)
# Prepared: 2026-06-16
# Sprint: PRODUCT-DEEPENING-GATE11-UPDATE-20260616
# Status: PREPARATION ONLY — NOT SUBMITTED — Human approval from Babar Raza required before submission

---

## 1. Format Identity

| Field | Value |
|-------|-------|
| Format ID | `zst` |
| Display name | Zstandard Compressed File |
| MIME type | `application/zstd` |
| Extension | `.zst`, `.tar.zst` |
| Source | IETF RFC 8878 (Informational, 2021-02-01) |
| Registry entry | `registry/format-registry.yaml` → format_id: zst |

---

## 2. Gate Status Summary

| Gate | Status | Evidence Location |
|------|--------|-------------------|
| G1 (Candidate Approval) | PASSED | `prototypes/by-format/zst/` exists |
| G2 (Spec Authority) | PASSED | IETF RFC 8878 acquired |
| G3 (Prototype Execution) | PASSED | `src/python/zst/` + 625 Python test functions |
| G4 (Parser Prototype) | PASSED | `src/python/zst/zst_codec.py` — frame parsing, magic byte check |
| G5 (Neutral Model) | PASSED | `probe_frame()` → metadata dict with frame count, sizes |
| G6 (Oracle Comparison) | PASSED | compress→decompress→verify tests pass |
| G7 (Fuzz/Security) | PASSED | 256MiB decompression guard, 2GiB window guard, magic byte validation |
| G8 (Security Review) | PASSED | Size guards, frame count limits, magic byte check |
| G9 (Dogfood) | PASSED | ZST compression/decompression used in dogfood pipelines |
| G10 (FOSS POC Complete) | PASSED (Python) | 625 Python test functions; compress/decompress/probe verified |
| G11-E (.NET prototype) | NOT_STARTED | No .NET track for ZST |
| G11-G (Commercial readiness) | NOT APPROVED | Requires Babar Raza approval |

**Claimed gate:** G10 (Python FOSS complete)
**Evidence-backed gate:** G10 (625 tests, full compress/decompress roundtrip)

---

## 3. Python FOSS Track Evidence

### 3A. Source Files

| File | Path | LOC |
|------|------|-----|
| zst_codec.py | `src/python/zst/zst_codec.py` | ~1210 |
| \_\_init\_\_.py | `src/python/zst/__init__.py` | ~100 |

### 3B. Test Evidence

| Metric | Value |
|--------|-------|
| Total Python test functions | **625** |
| Test files | 63 files in `tests/python/zst/` |
| Pre-existing import errors | 13 (stale installed venv package — not test failures) |
| Actual test failures | 0 (when run with sys.path source import) |

### 3C. Key Capabilities Implemented

| Capability | Function | Status |
|------------|----------|--------|
| Compress bytes | `compress_bytes(data)` | PASS |
| Decompress bytes | `decompress_bytes(data)` | PASS |
| Compress file | `compress_file(src, dest)` | PASS |
| Decompress file | `decompress_file(src, dest)` | PASS |
| Validate roundtrip | `validate_roundtrip(path)` | PASS |
| Probe frame | `probe_frame(data)` | PASS |
| Validate file | `validate_file(path)` | PASS |
| Get frame sizes | `zst_frame_sizes(path)` | PASS |
| Compression ratio | `zst_compression_ratio(path)` | PASS |
| Frame count | `zst_frame_count(path)` | PASS |
| Is single frame | `zst_is_single_frame(path)` | PASS |
| Max frame size | `zst_max_frame_size(path)` | PASS |
| Decompressed/compressed ratio | `zst_decompressed_to_compressed_ratio(path)` | PASS (new) |

---

## 4. .NET Commercial Track Evidence

| Capability | Status |
|------------|--------|
| .NET source | NOT_STARTED |
| ZstandardArchive (Aspose.ZIP) | Available but not implemented in this track |

**Note:** ZST commercial value is archive handling (decompress/extract), not document conversion. Commercial track is lower priority than FODS/FODT.

---

## 5. Security Review Summary

| Control | Implementation |
|---------|---------------|
| Max decompressed size | 256 MiB guard |
| Window size guard | 2 GiB maximum |
| Magic byte check | `\xFD\x2F\xB5\x28` validated |
| Frame count limit | Configurable |
| Malformed input tests | Pass |

---

## 6. Remaining Gaps Before Full G11

| Gap | Type | Priority |
|-----|------|----------|
| .NET commercial track | Commercial | LOW (archive handler, not document converter) |
| G11-G approval | EXTERNAL_GATE | Babar Raza decision |

---

## 7. What Babar Raza Must Decide

1. Whether ZST commercial (.NET) track is required for G11-G approval
2. Whether Python FOSS track alone satisfies commercial release criteria
3. Approval of package publication to PyPI

---

## 8. Evidence File Locations

| Artifact | Location |
|----------|----------|
| Python source | `src/python/zst/` (zst_codec.py, \_\_init\_\_.py) |
| Python tests | `tests/python/zst/` (63 files, 625 test functions) |
| Format registry | `registry/format-registry.yaml` → format_id: zst |
| Completion matrix | `registry/format-completion-matrix.yaml` → format_id: zst |
| Sample files | `samples/by-format/zst/valid/` |
| Dogfood tests | `tests/python/dogfood/test_dogfood_zst_frame_ndjson_export.py` etc. |
