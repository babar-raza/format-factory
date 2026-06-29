# ZST — Gate 11 Commercial Readiness Packet
# Prepared by: Agent (agent-owned preparation — submission requires human authorization)
# Prepared: 2026-06-16
# Updated: 2026-06-20 — per-criterion P1-P11 assessment added (TC-IMPL-003)
# Updated: 2026-06-21 — G11-E corrected to PASS (30 .NET tests, src/net/zst/); test count updated to 4,149; P5 collection error fixed (test_r115 import fixed, 11 tests now pass)
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
| G3 (Prototype Execution) | PASSED | `src/python/zst/` + 4,149 Python tests |
| G4 (Parser Prototype) | PASSED | `src/python/zst/zst_codec.py` — frame parsing, magic byte check |
| G5 (Neutral Model) | PASSED | `probe_frame()` → metadata dict with frame count, sizes |
| G6 (Oracle Comparison) | PASSED | compress→decompress→verify tests pass |
| G7 (Fuzz/Security) | PASSED | 256MiB decompression guard, 2GiB window guard, magic byte validation |
| G8 (Security Review) | PASSED | Size guards, frame count limits, magic byte check |
| G9 (Dogfood) | PASSED | ZST compression/decompression used in dogfood pipelines; installed_workflow=PASS |
| G10 (FOSS POC Complete) | PASSED (Python) | 4,149 Python tests; compress/decompress/probe verified |
| G11-E (.NET prototype) | PASS | `src/net/zst/` exists; 30/30 .NET tests pass (`tests/net/zst/ZstParserTests.cs`) |
| G11-G (Commercial readiness) | NOT APPROVED | Requires Babar Raza approval — TRUE_EXTERNAL_GATE |

**Claimed gate:** G10 (Python FOSS complete) + G11-E (.NET prototype complete)
**Evidence-backed gate:** G10 + G11-E (4,149 Python tests + 30 .NET tests)

---

## 3. Python FOSS Track Evidence

### 3A. Source Files

| File | Path | LOC |
|------|------|-----|
| zst_codec.py | `src/python/zst/zst_codec.py` | 1,558 (post-heal) |
| zst_analytics.py | `src/python/zst/zst_analytics.py` | 4,604 (extracted) |
| \_\_init\_\_.py | `src/python/zst/__init__.py` | ~10 (dynamic __all__) |

**Note (2026-06-18 healing):** `zst_analytics.py` extracted from `zst_codec.py` during analytics separation sprint. `zst_codec.py` reduced from 4,210 to 1,558 LOC. `__init__.py` now uses dynamic `__all__` (3 lines) replacing 760-line explicit list.

### 3B. Test Evidence

| Metric | Value |
|--------|-------|
| Total Python tests PASS | **4,149** |
| Test files | tests/python/zst/ |
| Pre-existing collection errors | 0 (test_r115 import fixed 2026-06-21: `src.python.zst.zst_codec` → `zst_codec`; 11 tests now PASS) |
| Actual test failures | 0 |
| Spec fact references (FACT-ZST-*) | 60 test files |

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
| Decompressed/compressed ratio | `zst_decompressed_to_compressed_ratio(path)` | PASS |
| Installed workflow | `installed_workflow` | PASS |

---

## 4. .NET Commercial Track Evidence

**CORRECTION (2026-06-21):** Previous assessment incorrectly stated G11-E as NOT_STARTED. Direct inspection confirms:

| Artifact | Status |
|----------|--------|
| `src/net/zst/` | EXISTS — full .NET ZST implementation |
| `tests/net/zst/ZstParserTests.cs` | EXISTS — 30 tests |
| .NET test result | **30/30 PASS** |

| Capability | Status |
|------------|--------|
| .NET source | IMPLEMENTED (`src/net/zst/`) |
| .NET tests | 30/30 PASS |

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

## 6. Gate 11 Criteria Assessment (registry/gate11-criteria.yaml)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| min_spec_facts_cited ≥ 3 | **PASS** | 60 test files reference FACT-ZST-*; 94 RFC 8878 verified facts in `.local/spec-cache/zst/rfc8878/` |
| min_api_coverage ≥ 0.6 | **PASS** | 7/7 FOSS APIs = 100% (compress_bytes, compress_file, decompress_bytes, decompress_file, probe, validate, installed_workflow) |
| foss_test_count_min ≥ 50 | **PASS** | 4,149 Python tests pass |
| commercial_test_count_min ≥ 10 | **PASS** | 30/30 .NET tests pass |
| parity_matrix_required | **PASS** | `tests/supervisor/test_spec_parity_zst_proof.py` exists; 94 spec facts from RFC 8878 workbench |
| dogfood_proof_required | **CONDITIONALLY_PASS** | ZST is a compression codec; inter-format dogfood not applicable; installed_workflow=PASS documented |
| no_placeholder_metadata | **PASS** | G11-G explicitly marked NOT APPROVED (not a placeholder; legitimate external gate status) |
| **G11-G execution approval** | **NOT APPROVED** | TRUE_EXTERNAL_GATE — Babar Raza authority only |

**Score: 6/7 agent-owned criteria PASS. 1 external gate pending.**
**Overall: CONDITIONALLY_READY**

---

## 7. Remaining Gaps Before Full G11

| Gap | Type | Priority |
|-----|------|----------|
| G11-G approval | EXTERNAL_GATE | Babar Raza decision (TRUE_EXTERNAL_GATE) |
| ~~P2: RFC-to-capability parity matrix~~ | ~~DOCUMENTATION~~ | **CLOSED 2026-06-21** — `reports/zst-parity/zst-rfc8878-capability-parity-matrix.md` created |
| ~~P8: Formal reduced-scope rationale~~ | ~~DOCUMENTATION~~ | **CLOSED 2026-06-21** — Documented in parity matrix §Excluded Scope Rationale |

---

## 8. What Babar Raza Must Decide

1. Whether Python FOSS track + .NET track satisfies G11-G commercial release criteria
2. Approval of package publication to PyPI
3. Confirmation that ZST scope (RFC 8878, no ODF QName hierarchy) makes P6/P7/P9/P10 not_applicable

---

## 9. Evidence File Locations

| Artifact | Location |
|----------|----------|
| Python source | `src/python/zst/` (zst_codec.py, zst_analytics.py, \_\_init\_\_.py) |
| Python tests | `tests/python/zst/` (4,149 tests) |
| .NET source | `src/net/zst/` |
| .NET tests | `tests/net/zst/ZstParserTests.cs` (30 tests) |
| Spec cache | `.local/spec-cache/zst/rfc8878/` (94 verified facts) |
| Format registry | `registry/format-registry.yaml` → format_id: zst |
| Sample files | `samples/by-format/zst/valid/` |
| Dogfood tests | `tests/python/dogfood/` (ZST-related) |
| Known failures | `registry/known-failure-ledger.yaml` (1 collection error, pre-existing) |

---

## 10. Per-Criterion Assessment — Section 13 Gate 11 Criteria (Added 2026-06-20, Revised 2026-06-21)

**Assessment method:** Direct codebase inspection as of 2026-06-21.
**Classification legend:** `evidence_verified` | `partial` | `not_started` | `blocked_external` | `not_applicable`
**Authority:** plans/strategic/spec-to-feature-radical-correction-plan.md Section 13
**ZST note:** ZST spec authority is IETF RFC 8878 (not ODF), so QName-based criteria (C11-C20, P6-P10) require adaptation.

### 10A. .NET Commercial Criteria (C1-C20) — ZST

**CORRECTION (2026-06-21):** C4 (≥10 .NET tests) is now evidence_verified. `src/net/zst/` exists with 30 .NET tests passing.

| Criterion | Classification | Note |
|-----------|----------------|------|
| C4 (.NET tests ≥ 10) | evidence_verified | 30/30 .NET tests pass (`tests/net/zst/ZstParserTests.cs`) |
| C1-C3, C5-C9 | partial/not_applicable | .NET implementation exists; fuller commercial API pending Babar Raza scope decision |
| C10 | blocked_external | Babar Raza must decide commercial release scope |

### 10B. Python FOSS Criteria (P1-P11)

| Criterion | Description | Classification | Note |
|-----------|-------------|----------------|------|
| P1 | Class-based model | partial | Function-based API appropriate for codec; no class model |
| P2 | Parity matrix | evidence_verified | **NEW (2026-06-21):** RFC-to-capability matrix created: `reports/zst-parity/zst-rfc8878-capability-parity-matrix.md`. 80% RFC 8878 sections COVERED; all MUST requirements PASS; 2 sections formally excluded with documented rationale. |
| P3 | capability_coverage ≥ 60% | evidence_verified | 14/14 capabilities PASS; 4,149 tests |
| P4 | Wheel buildable | evidence_verified | Built and installed-workflow PASS (2026-06-18) |
| P5 | 0 collection errors | evidence_verified | **FIXED (2026-06-21):** test_r115_zst_file_roundtrip.py import updated from `src.python.zst.zst_codec` to direct `zst_codec`. 11/11 tests now pass. 0 collection errors. |
| P6 | Spec-prefix hierarchy | not_applicable | RFC 8878 has no namespace hierarchy |
| P7 | Reduced parity matrix | not_applicable | No QName-to-code map for RFC-based format |
| P8 | Missing class rationale | evidence_verified | **NEW (2026-06-21):** Formal reduced-scope rationale documented in `reports/zst-parity/zst-rfc8878-capability-parity-matrix.md` §Excluded Scope Rationale. Dictionary compression and skippable frame creation formally excluded with reasons. |
| P9 | Dict/function API is compat only | not_applicable | Function API IS the appropriate model for a codec |
| P10 | Wrappers delegate to canonical | not_applicable | No ODF model migration planned |
| P11 | Parity validators wired | partial | TC-GUARD-001, V42 apply to ZST |

**P1-P11 Overall: 5 evidence_verified (P2/P3/P4/P5/P8), 2 partial (P1/P11), 0 not_started, 4 not_applicable** (updated 2026-06-21: P2/P8 upgraded to evidence_verified; P5 upgraded 2026-06-21 — collection error fixed)

### 10C. Readiness Summary

| Track | evidence_verified | partial | not_started | blocked_external | not_applicable | Readiness (applicable) |
|-------|-------------------|---------|-------------|------------------|----------------|------------------------|
| .NET C1-C20 | 1 (C4) | varies | 0 | 1 (C10) | 18 | 50% of applicable |
| Python P1-P11 | 5 | 2 | 0 | 0 | 4 | 71.4% of applicable (updated 2026-06-21: P5 fixed) |

**Gate 11 status:** G10 CONFIRMED + G11-E CONFIRMED. G11-G NOT APPROVED — requires Babar Raza decision.

**Scoring target (Section 14):** ZST target is 20/25. Current: REVIEWABLE_WITH_LIMITATIONS.

**This assessment does NOT approve Gate 11. Babar Raza is the only approver.**

---

*End of ZST Gate 11 Readiness Packet*
*Agent-prepared 2026-06-16. Per-criterion assessment added 2026-06-20 (TC-IMPL-003).*
*G11-E corrected to PASS 2026-06-21 (30 .NET tests, src/net/zst/ confirmed). Test count updated to 4,149.*
*P2/P8 criteria upgraded to evidence_verified 2026-06-21 — RFC parity matrix and reduced-scope rationale created.*
*This document does NOT approve Gate 11. Gate 11 approval requires Babar Raza decision.*
