# Requirement Authority Lifecycle
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

A requirement goes through 5 stages before it can be used in a production context pack.
Each stage transition is recorded and irreversible (rejections are archived, not deleted).

---

## Stage 1 — Extraction (candidate_requirement)

**Trigger:** RequirementExtractor processes normalized_artifact
**State:** candidate_requirement (H)
**Record:**
```json
{
  "req_id": "req-<format>-<seq>",
  "text": "The frame header MUST contain a magic number of 0xFD2FB528",
  "type": "MUST",
  "source_snapshot_id": "<sha256>",
  "section_ref": "3.1.1",
  "extractor_version": "1.0",
  "status": "candidate_requirement",
  "extracted_at": "<ISO datetime>",
  "stale": false
}
```
**Authority:** This is a candidate only. Cannot be used in production context packs.
**Transition to Stage 2:** SpecVerifier.verify(req_id) called

---

## Stage 2 — Verification (verified_requirement)

**Trigger:** SpecVerifier confirms requirement against source text
**State:** verified_requirement (I)
**Verification methods:**
- EXACT_MATCH — requirement text found verbatim in source section
- SEMANTIC_MATCH — requirement text semantically equivalent to source (documented evidence required)
- INFERRED — requirement logically follows from multiple source sections (all sections cited)
**Record additions:**
```json
{
  "status": "verified_requirement",
  "verification_method": "EXACT_MATCH",
  "verifier_version": "1.0",
  "verified_at": "<ISO datetime>",
  "provenance_hash": "<sha256 of source_section_text + section_ref>",
  "verification_confidence": "HIGH|MEDIUM|LOW"
}
```
**Authority:** Verified requirements are authoritative for production use.
**Rejection path:** If verification fails, requirement stays at candidate_requirement (H)
with rejection_record appended.

---

## Stage 3 — Graph Inclusion (RequirementGraph)

**Trigger:** RequirementGraph.add(verified_req_id, format_id)
**Effect:** Requirement becomes a node in the cross-format dependency DAG
**Cross-format edges:** Created when two formats share a data type or error behavior
**Authority:** Graph enables cross-format requirement comparison and gap detection

---

## Stage 4 — Context Pack Assembly (context_pack)

**Trigger:** ContextPackBuilder selects verified requirements for a task
**State:** verified requirements → included in context_pack (J)
**Selection criteria:**
- request_type matches requirement's applicability
- requirement not stale (source sha256 unchanged)
- requirement verification_confidence >= threshold for task type
**Authority:** Included requirements are the authoritative spec basis for the consuming task.

---

## Stage 5 — Usage and Coverage Recording

**Trigger:** Stream consumes context pack
**State:** usage_record (K) created; coverage_record (L) generated
**Usage record:** append-only JSONL entry
**Coverage record:** which requirements in the task were addressed vs missed

---

## Requirement Rejection Rules

| Rejection Reason | Action |
|------------------|--------|
| Source text not found | Stays at H; rejection_record with reason |
| Source sha256 mismatch | Stays at H; source_sha256_mismatch flagged |
| Ambiguous type (MUST vs SHOULD) | Stays at H; manual review required |
| Duplicate of existing verified req | Stays at H; duplicate_of field set |
| Source license quarantined | Stays at H; license_blocked flag set |

---

## Staleness Rules for Requirements

| Trigger | Effect on Requirements |
|---------|----------------------|
| source sha256 changes | All requirements with that source_snapshot_id → stale = true |
| normalizer version changes | All candidate requirements → re-extract required |
| verifier version changes | Verified requirements stay valid (version recorded in provenance) |
| index version changes | No effect on requirements directly |

---

## Provenance Chain

```
raw_snapshot (sha256: abc123)
  └─[SpecParser v1.0]─► parsed_artifact (pid-001)
      └─[SpecNormalizer v1.0]─► normalized_artifact (nid-001)
          └─[RequirementExtractor v1.0]─► candidate_requirement (req-zst-001)
              └─[SpecVerifier v1.0, EXACT_MATCH, section 3.1.1]─► verified_requirement (req-zst-001)
                  └─[provenance_hash: sha256("magic number...section 3.1.1")]
```

This chain allows any verified requirement to be traced to its original source bytes.
