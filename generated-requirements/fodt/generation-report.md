# FODT Generated Requirements — Generation Report
**Lane R4 — FODT AI-Generated Commercial Requirements**
**Date:** 2026-05-13
**Generator:** claude-sonnet-4-6 (via agent, local evidence retrieval)
**Pipeline:** AI-GENERATED-FORMAT-REQUIREMENTS-PIPELINE v1.0

---

## Generation Summary

| Artifact | Requirements | Status |
|----------|-------------|--------|
| commercial-requirements.yaml | 17 requirements (FODT-REQ-*) | COMPLETE |
| object-model-requirements.yaml | 4 entities (FODT-ENT-*) | COMPLETE |
| save-edit-requirements.yaml | 5 requirements (FODT-SE-*) | COMPLETE |
| conversion-requirements.yaml | 4 requirements (FODT-CONV-*) | COMPLETE |
| traceability-map.yaml | 5 PG mappings | COMPLETE |

**Total requirements:** 26 across all files
**ACCEPTED_FOR_VERTICAL_SLICE:** 20
**Deferred/future:** 5 (FODT-SE-030, FODT-CONV-001..004)
**AI_PROPOSAL source types:** 0

---

## Input Sources Used

| Source | Path | Used For |
|--------|------|---------|
| Existing parser | src/net/fodt/FodtParser.cs | Load requirements, security |
| Existing document | src/net/fodt/FodtDocument.cs | Object model |
| Existing model | src/net/fodt/Model/ (FodtBody, FodtParagraph) | Entities |
| Existing writer | src/net/fodt/FodtWriter.cs | Save requirements |
| Existing tests | tests/net/fodt/ (EditTests, RoundtripTests, OracleTests) | Test evidence |
| Verified facts | acquisition-packs/fodt/verified-facts.yaml | FODT structural facts |
| Neutral model | schemas/neutral-model/fodt/model.yaml | Structural mapping |
| Tier map | acquisition-packs/fodt/tier-map.yaml | Feature scope |
| Implementation reqs | acquisition-packs/fodt/implementation-requirements.yaml | IR-FODT-* |
| ODF 1.3 spec | §3.1.2, §3.2, §5.1.2, §5.1.3, §5.5, §9.1 | MIME, text, list, table |

---

## Source Evidence Distribution

| source_type | Count |
|-------------|-------|
| EXISTING_SOURCE | 10 |
| TEST_EVIDENCE | 6 |
| VERIFIED_FACT | 5 |
| SPEC | 4 |
| PRODUCT_DECISION | 3 |
| AI_PROPOSAL | 0 |

---

## Critical Requirement — IR-FODT-003

**FODT-REQ-040: Iterative list traversal — MUST NOT be recursive**

FODT documents can contain deeply nested `text:list` elements inside `text:list-item` children. Recursive traversal risks stack overflow on adversarial inputs. The implementation MUST use iterative traversal with an explicit `Stack<T>`. This requirement is in the `critical_requirements` map in `traceability-map.yaml` and enforced via Lane R5 verifier.

---

## Capability Level Coverage

| Level | Description | Requirements |
|-------|-------------|-------------|
| C0 | Detection / validation | FODT-REQ-001, 002, 003 |
| C1 | Metadata extraction | FODT-REQ-004, 005 |
| C2 | Structure enumeration | FODT-REQ-006, 007, 008 |
| C4 | Object model | FODT-REQ-010, 011, 012, 013, 040 |
| C6 | Edit | FODT-REQ-020 |
| C7 | Save / round-trip | FODT-REQ-030, 031 |

---

## Vertical Slice Scope (C7 Target)

The vertical slice covers a complete load→edit→save pipeline for FODT documents:

1. **Load:** File validation, security guards, MIME detection, metadata, paragraph/list/table enumeration
2. **Object model:** FodtDocument → FodtBody → FodtParagraph hierarchy (+ list traversal, table traversal)
3. **Edit:** Paragraph text edit via SetText()
4. **Save:** Round-trip save, edit persistence, opaque node preservation
5. **Critical safety:** IR-FODT-003 iterative list traversal

This is the minimum viable commercial product scope for FODT at C7.

---

## Lane R5 Verifier Verdict

**LANE_R5_PASS** — See `generated-requirements/fodt/verifier-review.yaml`
