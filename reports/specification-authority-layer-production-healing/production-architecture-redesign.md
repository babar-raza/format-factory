# Production Architecture Redesign — Specification Authority Layer
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Architecture Overview

The Specification Authority Layer is a production-grade system making file-format specifications
reliably available to agents and LLMs with full traceability, determinism, and anti-bypass enforcement.

```
Input (external spec sources)
  │
  ▼
[SpecSourceRegistry] ──── source trust gate ────────────────────────────────────────┐
  │                                                                                   │
  ▼                                                                                   │
[SpecVault] ──── SHA-256 content addressing, immutable snapshots ──────────────────┐ │
  │                                                                                 │ │
  ▼                                                                                 │ │
[SpecParser] ──── format-specific structured AST ─────────────────────────────────┐│ │
  │                                                                                ││ │
  ▼                                                                                ││ │
[SpecNormalizer] ──── canonical cross-format schema ──────────────────────────────┘│ │
  │                                                                                 │ │
  ▼                                                                                 │ │
[SpecIndexer] ──── versioned index with staleness tracking ───────────────────────┘ │
  │                                                                                   │
  ▼                                                                                   │
[SpecDigestor] ──── compressed digest for LLM context management ───────────────────│
  │                                                                                   │
  ▼                                                                                   │
[RequirementExtractor] ──── structured requirement extraction ──────────────────────│
  │                                                                                   │
  ▼                                                                                   │
[SpecVerifier] ──── provenance verification gate (H→I) ─────────────────────────────│
  │                                                                                   │
  ▼                                                                                   │
[RequirementGraph] ──── cross-format dependency DAG ────────────────────────────────│
  │                                                                                   │
  ▼                                                                                   │
[ContextPackBuilder] ──── deterministic pack with manifest.sha256 ──────────────────│
  │                                                                                   │
  ▼                                                                                   │
[SpecGovernanceRuntime] ──── stream enforcement, anti-bypass ────────────────────────┘
  │
  ▼
Output (context packs to Mainstream, Acceleration, Skills, Supervisor streams)
```

---

## Subsystem Specifications

### 1. SpecSourceRegistry

**Role:** Authoritative registry of all approved specification sources.
**Inputs:** Source URL, license type, submitter, rationale
**Outputs:** source_id (UUID), registration_record, approval_status
**Key fields:** source_id, url, license (PUBLIC_SPEC | OPEN_SOURCE | PROPRIETARY_RESTRICTED |
PENDING_REVIEW | QUARANTINED), registration_date, approved_by, sha256_at_registration
**Rules:**
- All sources must transition source_candidate → registered_source before SpecVault ingestion
- PROPRIETARY_RESTRICTED sources: quarantine raw snapshot; document fetch-blocker
- PENDING_REVIEW sources: allowed for ingestion but flagged in context packs as UNCONFIRMED_LICENSE
**Storage:** .local/spec-source-registry/sources.json (append-only per registration)

---

### 2. SpecVault

**Role:** Immutable raw snapshot store with SHA-256 content addressing.
**Inputs:** Registered source (source_id + URL)
**Outputs:** snapshot_id (= SHA-256 of content), snapshot_path, ingestion_record
**Key fields:** snapshot_id (sha256), source_id, ingested_at, byte_size, content_type, url_at_ingest
**Rules:**
- Write-once: once a sha256 is stored, it is never overwritten
- Read by content hash only (not by URL)
- URL may return different content over time; sha256 pins the version
- Snapshot record includes ingested_at timestamp (excluded from semantic hash comparison)
**Storage:** .local/spec-vault/{first2}/{sha256}.bin + index .local/spec-vault/index.json

---

### 3. SpecParser

**Role:** Format-specific parser producing structured JSON from raw spec snapshot.
**Inputs:** snapshot_id (sha256), format_hint (optional)
**Outputs:** parsed_artifact_id, parsed_artifact_path (JSON)
**Output schema:**
```json
{
  "snapshot_id": "<sha256>",
  "format": "rfc|man_page|odf_spec|project_docs",
  "version": "<parser_version>",
  "sections": [{"id": "s1", "title": "...", "content": "...", "level": 1}],
  "tables": [{"id": "t1", "section_id": "s1", "rows": [...]}],
  "examples": [{"id": "e1", "section_id": "s1", "code": "..."}]
}
```
**Rules:** Parser version must be recorded; output is deterministic for same input sha256.

---

### 4. SpecNormalizer

**Role:** Cross-format normalization to canonical schema.
**Inputs:** parsed_artifact_id
**Outputs:** normalized_artifact_id, normalized_artifact_path (JSON)
**Output schema:**
```json
{
  "parsed_artifact_id": "<id>",
  "normalizer_version": "<version>",
  "requirement_candidates": [
    {"id": "r1", "text": "...", "section_ref": "s1", "type": "MUST|SHOULD|MAY|INFORMATIVE"}
  ],
  "data_types": [{"name": "...", "description": "...", "section_ref": "s2"}],
  "error_codes": [{"code": "...", "meaning": "...", "section_ref": "s3"}]
}
```
**Rules:** Normalization is deterministic; type tagging (MUST/SHOULD/MAY) from RFC 2119 keywords.

---

### 5. SpecIndexer

**Role:** Lexical and semantic index over normalized artifacts.
**Inputs:** normalized_artifact_id, index_version
**Outputs:** index_id, index_record
**Key fields:** index_id, normalized_artifact_id, index_version, indexed_at, term_count, stale=false
**Rules:**
- Index version increments on algorithm change
- If normalized_artifact updated (source sha256 changed): index marked stale
- Re-indexing required before context pack build for stale indexes

---

### 6. SpecDigestor

**Role:** Compressed digest generation for LLM context window management.
**Inputs:** normalized_artifact_id, target_token_budget
**Outputs:** digest_artifact_id, digest_path, manifest.sha256 linkage
**Key fields:** source_snapshot_id, token_budget, compression_ratio, digest_sha256
**Rules:**
- Same normalized_artifact + same token_budget → same digest_sha256
- Digest does NOT strip requirement_candidates (only prose/examples compressed)

---

### 7. RequirementExtractor

**Role:** Structured requirement extraction from normalized artifacts.
**Inputs:** normalized_artifact_id
**Outputs:** [candidate_requirement_id, ...], extraction_record
**Key fields per requirement:** req_id, text, type (MUST/SHOULD/MAY), source_snapshot_id,
section_ref, extractor_version, status = candidate_requirement
**Rules:**
- All extracted requirements start as candidate_requirement (state H)
- Provenance required: source_snapshot_id + section_ref + extractor_version

---

### 8. SpecVerifier

**Role:** Requirement verification against spec source with provenance.
**Inputs:** candidate_requirement_id
**Outputs:** VerificationResult — verified_requirement_id or rejection
**Key fields:** req_id, verification_method, verifier_version, verifier_id, verified_at,
source_sha256, section_ref, provenance_hash
**Rules:**
- State gate: candidate_requirement (H) → verified_requirement (I) requires SpecVerifier
- Unverified requirements CANNOT be used in production context packs
- Rejection creates a rejection record (reason + timestamp); requirement stays at H

---

### 9. RequirementGraph

**Role:** Dependency graph of requirements across specs.
**Inputs:** [verified_requirement_id, ...], format_id
**Outputs:** graph_id, graph_record (DAG)
**Key fields:** nodes (requirement nodes), edges (dependency/conflict/complement relationships),
cross_format_edges (via normalized_artifact_id)
**Rules:**
- Only verified_requirements (state I) as graph nodes
- Cross-format edges require both endpoints to be verified

---

### 10. ContextPackBuilder

**Role:** Deterministic context pack assembly with manifest.sha256.
**Inputs:** [source_sha256, ...], request_type, index_version
**Outputs:** ContextPack — context_pack_id, manifest.sha256, pack_contents
**Determinism contract:**
```
canonical_input = sorted(source_sha256_list) + "|" + request_type + "|" + index_version
manifest.sha256 = sha256(canonical_input + sha256(pack_contents))
```
Timestamps excluded from semantic hash comparison.
**Rules:**
- Same canonical_input → same manifest.sha256 (verified by regression category D)
- Context pack rejected if any included source is stale
- Context pack rejected if manifest.sha256 absent or not 64-char hex

---

### 11. SpecGovernanceRuntime

**Role:** Enforcement of ai-authority-boundary at all handoffs.
**Inputs:** handoff event (stream, evidence fields)
**Outputs:** ValidationResult (PASS/FAIL/WARN + reason)
**Enforcement rules:**
- Mainstream: requires context_pack_id + requirement_ids + source_snapshot_ids
- Acceleration: same; ai_draft label required for AI-generated content
- Skills: context_pack_id + requirement_ids + usage_id required
- Supervisor: validates context_pack_id in evidence declarations; staleness check
**Anti-bypass rules:**
- Ad-hoc URL citation without registered source → FAIL
- Memory-only spec claim → FAIL (no source_ref)
- Raw AI summary without source_refs → requires ai_draft label
- Unverified requirement in production context pack → FAIL
- Context pack without manifest.sha256 → FAIL

---

## Pipeline Data Flow Summary

```
URL → [SpecSourceRegistry] → source_id
source_id → [SpecVault] → snapshot_id (sha256)
snapshot_id → [SpecParser] → parsed_artifact_id
parsed_artifact_id → [SpecNormalizer] → normalized_artifact_id
normalized_artifact_id → [SpecIndexer] → index_id
normalized_artifact_id → [SpecDigestor] → digest_artifact_id
normalized_artifact_id → [RequirementExtractor] → [candidate_req_ids]
candidate_req_id → [SpecVerifier] → verified_req_id
[verified_req_ids] → [RequirementGraph] → graph_id
[source_sha256s] → [ContextPackBuilder] → context_pack (manifest.sha256)
context_pack → [SpecGovernanceRuntime] → validated handoff
```
