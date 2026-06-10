# Preserve vs Redesign Matrix — Specification Authority Layer
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Decision Framework

For each subsystem: PRESERVE (existing approach correct), REDESIGN (structural change needed),
or NEW (subsystem did not previously exist).

---

## Matrix

| Subsystem | Decision | Rationale |
|-----------|----------|-----------|
| SpecSourceRegistry | NEW | Did not exist; source trust chain was absent |
| SpecVault | REDESIGN | Existed as URL fetch; needs SHA-256 content addressing + immutability |
| SpecParser | PRESERVE | Format-specific parsing approach is correct; needs schema output standardization |
| SpecNormalizer | NEW | Did not exist; cross-format normalization was missing |
| SpecIndexer | REDESIGN | Existed as ad-hoc search; needs versioned index with staleness tracking |
| SpecDigestor | PRESERVE | Compression/summarization approach correct; needs manifest.sha256 integration |
| RequirementExtractor | PRESERVE | Extraction approach correct; needs provenance linkage |
| SpecVerifier | REDESIGN | Existed implicitly; needs formal state gate (H→I) and provenance proof |
| RequirementGraph | PRESERVE | Graph structure correct; needs cross-format edge support |
| ContextPackBuilder | REDESIGN | Existed; needs determinism contract (same inputs → same manifest.sha256) |
| SpecGovernanceRuntime | NEW | Did not exist; enforcement at stream boundaries was absent |

---

## PRESERVE — Detailed Justification

### SpecParser
- Format-specific parsing is architecturally correct (ZST RFC → AST, Netpbm man pages → sections)
- Preserving parser contracts preserves existing work
- Change: output must conform to canonical JSON schema

### SpecDigestor
- LLM context window management through compression is correct approach
- Preserving reduces regression risk
- Change: output must include manifest.sha256 linkage for determinism tracking

### RequirementExtractor
- Requirement extraction from structured documents is correct approach
- Preserving existing extraction patterns
- Change: each extracted requirement must carry source_sha256, section_ref, extractor_version

### RequirementGraph
- DAG model for requirement dependencies is correct
- Preserving graph structure and traversal API
- Change: cross-format edge support via normalized_artifact_id references

---

## REDESIGN — Detailed Justification

### SpecVault
- **Problem:** URL fetch on every use; no content addressing; not immutable
- **Redesign:** Write-once store keyed by SHA-256; read by content hash; never overwrite
- **Interface change:** `ingest(url, license) → snapshot_id (sha256)` + `read(sha256) → bytes`

### SpecIndexer
- **Problem:** Ad-hoc search index; no version tracking; no staleness signal
- **Redesign:** Versioned index with index_version; re-index on normalized_artifact update; stale flag
- **Interface change:** `index(normalized_artifact_id, version) → index_id` + staleness check

### SpecVerifier
- **Problem:** Implicit verification without formal state gate; provenance not recorded
- **Redesign:** Formal H→I state gate; verification must produce proof (source_sha256 + section_ref)
- **Interface change:** `verify(candidate_req_id) → VerificationResult(verified_req_id, provenance)`

### ContextPackBuilder
- **Problem:** Context packs not deterministic; different runs produce different outputs
- **Redesign:** Canonical input fingerprint (sorted source_sha256s + request_type + index_version)
  → stable manifest.sha256
- **Interface change:** `build(sources, request_type, index_version) → ContextPack(manifest.sha256)`

---

## NEW — Detailed Justification

### SpecSourceRegistry
- **Why new:** Source trust chain completely absent
- **Design:** Registry of approved spec sources with source_id, url, license, registration_date, sha256
- **Gate:** All sources must be registered before SpecVault ingestion
- **Interface:** `register(url, license) → source_id` + `is_approved(url) → bool`

### SpecNormalizer
- **Why new:** Cross-format normalization completely absent
- **Design:** Converts format-specific SpecParser output to canonical JSON schema
  (section_type, requirements, tables, examples, references)
- **Interface:** `normalize(parsed_artifact_id) → normalized_artifact_id`

### SpecGovernanceRuntime
- **Why new:** Enforcement at stream boundaries completely absent
- **Design:** Runtime checks at every handoff; validates context_pack_id, staleness, ai_draft misuse
- **Interface:** `validate_handoff(stream, evidence) → ValidationResult(PASS/FAIL, reason)`
