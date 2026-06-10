# Regression Control Suite — 9 Categories, 42+ Tests
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The regression control suite covers all spec layer failure modes. Minimum: 42 test cases
across 9 categories (A through I). Tests are defined here as specifications; implementation
goes in tests/specification-authority-layer/ during MWP execution.

---

## Category A — Schema Validation (5 tests)

Tests that spec artifacts match declared JSON schema.

| ID | Test | Expected |
|----|------|---------|
| A-01 | parsed_artifact conforms to parser output schema | PASS: validates |
| A-02 | normalized_artifact conforms to normalizer schema | PASS: validates |
| A-03 | candidate_requirement has all required fields (req_id, text, type, source_snapshot_id, section_ref) | PASS: validates |
| A-04 | verified_requirement has provenance_hash and verification_method | PASS: validates |
| A-05 | context_pack manifest has manifest_sha256 as 64-char hex | PASS: validates |

---

## Category B — Provenance (5 tests)

Tests that all requirements trace to registered_source with sha256.

| ID | Test | Expected |
|----|------|---------|
| B-01 | Every verified requirement has source_snapshot_id in SpecVault | PASS: all present |
| B-02 | Every verified requirement has section_ref (non-empty string) | PASS: all present |
| B-03 | provenance_hash = sha256(section_text + section_ref) is reproducible | PASS: stable |
| B-04 | Requirement with unregistered source rejected by SpecSourceRegistry gate | PASS: rejection recorded |
| B-05 | Context pack source_sha256s all present in SpecVault | PASS: all found |

---

## Category C — Parser Round-trip (5 tests)

Tests parser determinism: raw_snapshot → parsed → re-serialized matches original.

| ID | Test | Expected |
|----|------|---------|
| C-01 | ZST spec: parse → serialize → parse produces identical structure | PASS: structures match |
| C-02 | Netpbm spec: parse → serialize → parse produces identical structure | PASS: structures match |
| C-03 | DIF spec: parse → serialize → parse produces identical structure | PASS: structures match |
| C-04 | Parser version recorded in parsed_artifact | PASS: version present |
| C-05 | Same snapshot_id → same parsed_artifact (deterministic) | PASS: sha256 stable |

---

## Category D — Context Pack Determinism (5 tests)

Tests that same inputs produce same manifest.sha256.

| ID | Test | Expected |
|----|------|---------|
| D-01 | Same source_sha256s + request_type + index_version → same manifest.sha256 (run twice) | PASS: equal |
| D-02 | Different source_sha256s → different manifest.sha256 | PASS: not equal |
| D-03 | Different request_type → different manifest.sha256 | PASS: not equal |
| D-04 | Different index_version → different manifest.sha256 | PASS: not equal |
| D-05 | Timestamp change does not affect manifest.sha256 | PASS: equal despite time change |

---

## Category E — Requirement Verifier Negatives (5 tests)

Tests that unverified requirements are not promoted to verified.

| ID | Test | Expected |
|----|------|---------|
| E-01 | candidate_requirement cannot be included in production context pack | PASS: rejected |
| E-02 | SpecVerifier rejects requirement when section text not found in source | PASS: rejection_record created |
| E-03 | SpecVerifier rejects requirement when source sha256 mismatches | PASS: rejection_record created |
| E-04 | Rejected requirement stays at H (candidate) with rejection_record | PASS: status unchanged |
| E-05 | Re-verification after correction creates new verified_requirement (not overwrite) | PASS: new req_id |

---

## Category F — Coverage Validator (5 tests)

Tests that coverage_record correctly identifies uncovered requirements.

| ID | Test | Expected |
|----|------|---------|
| F-01 | Coverage audit of ZST implementation identifies at least 3 addressed requirements | PASS: count >= 3 |
| F-02 | Coverage audit correctly reports missed requirements | PASS: gaps listed |
| F-03 | Coverage ratio = addressed / total_in_pack | PASS: ratio correct |
| F-04 | Coverage record written to usage ledger as type=coverage | PASS: record present |
| F-05 | Zero-coverage task (no requirement addressed) produces coverage_ratio=0.0 | PASS: ratio = 0.0 |

---

## Category G — Four-Stream Integration (5 tests)

Tests that handoff gates reject missing context_pack_id.

| ID | Test | Expected |
|----|------|---------|
| G-01 | Mainstream handoff without context_pack_id → FAIL: MISSING_CONTEXT_PACK_ID | PASS: rejected |
| G-02 | Acceleration handoff without ai_draft label on AI output → FAIL: UNLABELED_AI_DRAFT | PASS: rejected |
| G-03 | Skills handoff without usage_id → FAIL: MISSING_USAGE_ID | PASS: rejected |
| G-04 | Valid mainstream handoff with all required fields → PASS | PASS: accepted |
| G-05 | Supervisor detects stale context_pack_id in evidence declaration → CONTRADICTION | PASS: flagged |

---

## Category H — Refresh/Staleness (5 tests)

Tests that stale artifacts trigger refresh; clean artifacts do not.

| ID | Test | Expected |
|----|------|---------|
| H-01 | Source sha256 change → all downstream artifacts (D–J) stale=true | PASS: all stale |
| H-02 | refresh_event created when staleness detected | PASS: event present |
| H-03 | Context pack build from stale source → FAIL: STALE_SOURCE_SHA256 | PASS: rejected |
| H-04 | After refresh, new context pack with new manifest.sha256 builds successfully | PASS: builds |
| H-05 | Clean source (sha256 unchanged) → no staleness propagation | PASS: no change |

---

## Category I — Anti-bypass (7 tests)

Tests that ad-hoc URL citations, memory-only claims, ai_draft bypasses are blocked.

| ID | Test | Expected |
|----|------|---------|
| I-01 | Ad-hoc URL citation (not in SpecSourceRegistry) in mainstream → FAIL: UNREGISTERED_SOURCE | PASS: rejected |
| I-02 | Memory-only spec claim (no source_ref) in mainstream → FAIL: UNSOURCED_CLAIM | PASS: rejected |
| I-03 | Raw AI summary without ai_draft label in spec authority position → FAIL: UNLABELED_AI_DRAFT | PASS: rejected |
| I-04 | ai_draft content in mainstream spec_authority (no verification) → FAIL: AI_DRAFT_CANNOT_BE_SPEC_AUTHORITY | PASS: rejected |
| I-05 | Context pack without manifest.sha256 → FAIL: MISSING_MANIFEST_SHA256 | PASS: rejected |
| I-06 | Unverified requirement in production context pack → FAIL: UNVERIFIED_REQUIREMENT_IN_PACK | PASS: rejected |
| I-07 | Valid claim with registered source, verified requirement, labeled content → PASS | PASS: accepted |

---

## Test Count Summary

| Category | Test Count |
|----------|-----------|
| A — Schema validation | 5 |
| B — Provenance | 5 |
| C — Parser round-trip | 5 |
| D — Context pack determinism | 5 |
| E — Requirement verifier negatives | 5 |
| F — Coverage validator | 5 |
| G — Four-stream integration | 5 |
| H — Refresh/staleness | 5 |
| I — Anti-bypass | 7 |
| **Total** | **47** |

47 tests defined across 9 categories. Minimum threshold: 42. Status: THRESHOLD_MET.
