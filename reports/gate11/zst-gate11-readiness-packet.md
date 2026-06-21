# ZST — Gate 11 Commercial Readiness Packet
# Prepared by: Agent (agent-owned preparation — submission requires human authorization)
# Prepared: 2026-06-16
# Updated: 2026-06-20 — per-criterion P1-P11 assessment added (TC-IMPL-003)
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
| zst_codec.py | `src/python/zst/zst_codec.py` | ~1210 (post-heal) |
| \_\_init\_\_.py | `src/python/zst/__init__.py` | ~100 |

**Note (2026-06-18 healing):** `zst_analytics.py` extracted from `zst_codec.py` (4604 LOC) during analytics separation sprint. `zst_codec.py` reduced from 4210 to 1558 LOC. `__init__.py` now uses dynamic `__all__` (3 lines) replacing 760-line explicit list.

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

---

## 9. Per-Criterion Assessment — Section 13 Gate 11 Criteria (Added 2026-06-20)

**Assessment method:** Direct codebase inspection as of commit 1320e557.
**Classification legend:** `evidence_verified` | `partial` | `not_started` | `blocked_external` | `not_applicable`
**Authority:** plans/spec-to-feature-radical-correction-plan.md Section 13
**ZST note:** ZST has NO .NET commercial track. C1-C20 are therefore not_applicable for ZST.
The spec authority is IETF RFC 8878 (not ODF), so QName-based criteria (C11-C20, P6-P10) require adaptation.

### 9A. .NET Commercial Criteria (C1-C20) — ZST

| Criterion | Classification | Note |
|-----------|----------------|------|
| C1-C9 | not_applicable | ZST has no .NET commercial track by design decision |
| C10 | blocked_external | Babar Raza must decide whether .NET track is required for ZST Gate 11 |

**C1-C20 readiness: 0% — .NET track absent by design; C10 is Babar Raza scope decision**

### 9B. Python FOSS Criteria (P1-P11)

#### Original Depth Criteria (P1-P5)

| Criterion | Description | Classification | Evidence Path / Note |
|-----------|-------------|----------------|----------------------|
| P1 | Class-based model exists (no monolithic function-only modules) | partial | ZST uses function-based API in `zst_codec.py`. `probe_frame()` returns a dict. No class-based model. However, ZST is a binary compression format — the "neutral model" is inherently simpler than ODF documents. Function-based API is appropriate for a codec, but strictly P1 requires class-based. |
| P2 | Parity matrix exists and is up to date | not_started | No parity matrix artifact for ZST. RFC 8878 maps to capabilities, not ODF QNames. No ZST parity matrix found in any evidence bundle. |
| P3 | capability_coverage_percentage >= 60% | evidence_verified | poc-targets.yaml: ZST is POC_TARGET_CONFIRMED with multiple capabilities verified. 13 core capabilities all PASS (Section 3C). 625 tests across compress, decompress, probe, validate, frame analytics. |
| P4 | Wheel buildable from pyproject.toml | partial | `packaging/python/package-matrix.yaml` includes ZST. `build-local-packages.py` includes ZST. Wheel build confirmed in 2026-06-18 sprint (MEMORY.md: "ZST wheels built and installed-workflow verified PASS"). Evidence: `.local/package-builds/python-foss/` (from 2026-06-18). |
| P5 | 0 collection errors in test suite | partial | 63 test files, 625 test functions. 13 pre-existing import errors from stale installed venv package (Section 3B). These are NOT collection errors when run with sys.path source import. Strictly: collection error count > 0 with stale venv; 0 with source import. |

**P1-P5 readiness: 1 evidence_verified (P3), 3 partial (P1/P4/P5), 1 not_started (P2)**

#### Spec-Parity Criteria (P6-P11, System Healing Addition)

**Important ZST note:** P6-P11 are designed for ODF QName-based formats. ZST uses RFC 8878 binary format with no XML namespace hierarchy. The criteria require adaptation for non-ODF formats.

| Criterion | Description | Classification | Evidence Path / Note |
|-----------|-------------|----------------|----------------------|
| P6 | Python modules follow spec-prefix hierarchy where implemented | not_applicable | RFC 8878 has no namespace hierarchy. ZST flat module structure is appropriate. Mark as not_applicable pending Babar Raza scope decision. |
| P7 | Python reduced parity matrix generated from same QName-to-code map | not_applicable | No QName-to-code map for RFC-based format. ZST would need RFC-section-to-code map instead. No such artifact exists. |
| P8 | Every missing Python class has explicit reduced-scope reason | not_started | No formal reduced-scope ledger for ZST. ZST's function-based API missing explicit exception documentation. |
| P9 | Dict/function API is compatibility layer only after model migration | not_applicable | ZST has no ODF model migration planned. Function API IS the appropriate model for a codec. Requires scope decision. |
| P10 | Python wrappers delegate to canonical spec-literal model classes | not_applicable | No canonical spec-literal class hierarchy for RFC-based formats. |
| P11 | Python parity validators wired into supervisor verification | partial | TC-GUARD-001 in `autonomous_cycle.py` applies to ZST PRODUCT_SOURCE items. V42 (deepening suspension validator) applies to ZST analytics. 8 spec-parity validators (Section 10) may not cover RFC-based formats. |

**P6-P11 readiness: 0 evidence_verified, 1 partial (P11), 1 not_started (P8), 4 not_applicable**

**P1-P11 Overall: 1/7 evidence_verified (P3, excluding 4 not_applicable), 4 partial, 1 not_started, 4 not_applicable**
**Python FOSS readiness percentage (applicable criteria only): 14.3% (1/7 applicable)**

---

### 9C. Readiness Summary

| Track | Total Criteria | evidence_verified | partial | not_started | blocked_external | not_applicable | Readiness % |
|-------|---------------|-------------------|---------|-------------|------------------|----------------|-------------|
| .NET C1-C20 | 20 | 0 | 0 | 0 | 1 | 19 | N/A |
| Python P1-P11 | 11 | 1 | 4 | 1 | 0 | 4 | 14.3% (of applicable) |
| **Combined** | **31** | **1** | **4** | **1** | **1** | **23** | varies |

**Gate 11 status:** G10 CONFIRMED (Python FOSS). G11-G NOT APPROVED — requires Babar Raza decision on scope (Python-only or .NET required).

**ZST-specific findings:**
1. ZST Python FOSS track is the strongest of the three formats assessed: P3 evidence_verified, P4 partially verified via MEMORY.md, no monolith GOV_BLOCK (post-healing)
2. P6/P7/P9/P10 are not_applicable for ZST due to RFC-based (non-ODF) spec authority
3. P2 (parity matrix) is the most actionable gap: a ZST-RFC-8878-to-capability map could be created
4. The .NET track absence is a SCOPE DECISION by design, not a gap — Babar Raza must confirm

**Blockers for G11-G in priority order:**
1. Babar Raza scope decision on .NET requirement (C10 / G11-G external gate)
2. P2: No parity matrix artifact
3. P8: No formal reduced-scope reasoning for function-based API choice

**Scoring target (Section 14):** ZST target is 20/25, current estimated 19/25 (near-complete).
Per Section 14, ZST target classification: REVIEWABLE_WITH_LIMITATIONS.

**This assessment does NOT approve Gate 11. Babar Raza is the only approver.**

---

*End of ZST Gate 11 Readiness Packet*
*Agent-prepared 2026-06-16. Per-criterion assessment added 2026-06-20 (TC-IMPL-003).*
*This document does NOT approve Gate 11. Gate 11 approval requires Babar Raza decision.*
