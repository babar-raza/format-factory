# Tool Implementations — 13 Tools
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

13 tools implement the Specification Authority Layer pipeline. Each tool specification
includes: purpose, inputs, outputs, validation, and error handling.
Implementation target: tools/specification-authority-layer/ (during MWP execution).

---

## Tool 1 — spec_source_registry

**Purpose:** Manage the registry of approved specification sources.
**Module:** `tools/specification-authority-layer/spec_source_registry.py`

**Inputs:**
- `--register url license [--submitter name] [--rationale text]`
- `--list` — list all registered sources
- `--check url` — check if URL is registered

**Outputs:**
- Registration: `sources.json` entry added to `.local/spec-source-registry/sources.json`
- List: JSON array of registered sources
- Check: `REGISTERED | NOT_REGISTERED`

**Validation:**
- URL must be reachable (HTTP 200) before registration
- License must be one of: PUBLIC_SPEC, OPEN_SOURCE, PROPRIETARY_RESTRICTED, PENDING_REVIEW
- Duplicate URL registration: warn + return existing source_id

**Error handling:**
- URL unreachable: register with `status=UNREACHABLE_AT_REGISTRATION` + warn
- Invalid license: exit 1 with INVALID_LICENSE error

---

## Tool 2 — spec_vault_ingest

**Purpose:** Ingest a registered source into the immutable spec vault.
**Module:** `tools/specification-authority-layer/spec_vault_ingest.py`

**Inputs:**
- `--source-id <source_id>` — registered source to ingest
- `--output-dir` — vault directory (default: `.local/spec-vault/`)

**Outputs:**
- `snapshot_id` (SHA-256 of content) — printed to stdout
- Snapshot file: `.local/spec-vault/{sha256[:2]}/{sha256}.bin`
- Index update: `.local/spec-vault/index.json`

**Validation:**
- Source must be in registered_source state
- SHA-256 computed from raw bytes; verified by re-read
- If sha256 already exists in vault: skip ingest, return existing snapshot_id

**Error handling:**
- Source not registered: exit 1, SOURCE_NOT_REGISTERED
- Fetch failure: exit 2, FETCH_FAILED + URL + HTTP status
- Write failure: exit 3, WRITE_FAILED

---

## Tool 3 — spec_parser

**Purpose:** Format-specific parser producing structured JSON from raw spec snapshot.
**Module:** `tools/specification-authority-layer/spec_parser.py`

**Inputs:**
- `--snapshot-id <sha256>` — snapshot to parse
- `--format [rfc|man_page|odf_spec|project_docs|auto]` (default: auto)

**Outputs:**
- `parsed_artifact_id` — printed to stdout
- JSON file: `.local/spec-artifacts/parsed/{parsed_artifact_id}.json`

**Validation:**
- Output must validate against parser output schema
- Parser version recorded in output
- Determinism: same snapshot_id → same parsed_artifact sha256

**Error handling:**
- Unknown format: exit 1, UNKNOWN_FORMAT (use --format to specify)
- Parse failure: exit 2, PARSE_FAILED + section/line reference

---

## Tool 4 — spec_normalizer

**Purpose:** Cross-format normalization to canonical JSON schema.
**Module:** `tools/specification-authority-layer/spec_normalizer.py`

**Inputs:**
- `--parsed-artifact-id <id>` — parsed artifact to normalize

**Outputs:**
- `normalized_artifact_id` — printed to stdout
- JSON file: `.local/spec-artifacts/normalized/{normalized_artifact_id}.json`

**Validation:**
- Output must contain: requirement_candidates, data_types, error_codes
- Each requirement_candidate must have: id, text, type (MUST/SHOULD/MAY/INFORMATIVE), section_ref
- Normalizer version recorded

**Error handling:**
- Invalid parsed artifact: exit 1, INVALID_PARSED_ARTIFACT
- Normalization partial: exit 0 with WARNING (partial output still written)

---

## Tool 5 — spec_indexer

**Purpose:** Build versioned lexical/semantic index over normalized artifacts.
**Module:** `tools/specification-authority-layer/spec_indexer.py`

**Inputs:**
- `--normalized-artifact-id <id>` — artifact to index
- `--index-version <int>` (default: current version from config)

**Outputs:**
- `index_id` — printed to stdout
- Index record: `.local/spec-artifacts/indexes/{index_id}.json`

**Validation:**
- Index record has: normalized_artifact_id, index_version, indexed_at, term_count, stale=false
- term_count >= 1

**Error handling:**
- Artifact not found: exit 1, NORMALIZED_ARTIFACT_NOT_FOUND
- Index already current: exit 0 + ALREADY_CURRENT (no re-index needed)

---

## Tool 6 — spec_digestor

**Purpose:** Compressed digest generation for LLM context window management.
**Module:** `tools/specification-authority-layer/spec_digestor.py`

**Inputs:**
- `--normalized-artifact-id <id>`
- `--target-tokens <int>` (default: 2000)
- `--mode [full|section_summaries|capsule]` (default: full)

**Outputs:**
- `digest_artifact_id` — printed to stdout
- Digest file: `.local/spec-artifacts/digests/{digest_artifact_id}.json`

**Validation:**
- Token count <= target_tokens (within 10% tolerance)
- All MUST requirements preserved (not compressed out)
- manifest_sha256 linkage present

**Error handling:**
- Cannot fit within token budget without removing MUST requirements: exit 2, TOKEN_BUDGET_TOO_SMALL
- Invalid mode: exit 1, INVALID_MODE

---

## Tool 7 — requirement_extractor

**Purpose:** Structured requirement extraction from normalized artifacts.
**Module:** `tools/specification-authority-layer/requirement_extractor.py`

**Inputs:**
- `--normalized-artifact-id <id>`

**Outputs:**
- List of `candidate_requirement_id`s — printed to stdout (one per line)
- Requirement files: `.local/spec-artifacts/requirements/{req_id}.json`

**Validation:**
- Each requirement has: req_id, text, type, source_snapshot_id, section_ref, extractor_version
- At least 1 requirement extracted (exit 0 with WARNING if 0 found)

**Error handling:**
- Artifact not found: exit 1, NORMALIZED_ARTIFACT_NOT_FOUND
- No requirements found: exit 0 with WARNING: NO_REQUIREMENTS_FOUND

---

## Tool 8 — spec_verifier

**Purpose:** Requirement verification against spec source with provenance.
**Module:** `tools/specification-authority-layer/spec_verifier.py`

**Inputs:**
- `--req-id <candidate_requirement_id>`
- `--method [exact_match|semantic_match|inferred]` (default: exact_match)

**Outputs:**
- `verified_requirement_id` — printed to stdout on success
- Updated requirement file with verification fields

**Validation:**
- provenance_hash = sha256(section_text + section_ref) — must be stable
- Verification method documented in requirement record
- On rejection: rejection_record appended to `.local/spec-artifacts/rejections/{req_id}.json`

**Error handling:**
- Requirement not found: exit 1, REQUIREMENT_NOT_FOUND
- Verification failed (text not found): exit 2, VERIFICATION_FAILED (rejection recorded)
- Source snapshot not in vault: exit 1, SOURCE_NOT_IN_VAULT

---

## Tool 9 — requirement_graph

**Purpose:** Build and query dependency graph of requirements across specs.
**Module:** `tools/specification-authority-layer/requirement_graph.py`

**Inputs:**
- `--add-req <verified_requirement_id> --format-id <id>`
- `--add-edge req-a req-b [--type DEPENDS_ON|CONFLICTS_WITH|COMPLEMENTS]`
- `--query --format-id <id>` — list requirements for format
- `--query --cross-format` — list cross-format edges

**Outputs:**
- Graph file: `.local/spec-artifacts/graphs/requirement-graph.json`
- Query results: JSON to stdout

**Validation:**
- Only verified_requirements (state I) as nodes
- Cross-format edges require both endpoints to be verified

**Error handling:**
- Unverified requirement: exit 1, UNVERIFIED_REQUIREMENT_CANNOT_BE_ADDED
- Duplicate edge: exit 0 with WARNING

---

## Tool 10 — context_pack_builder

**Purpose:** Deterministic context pack assembly with manifest.sha256.
**Module:** `tools/specification-authority-layer/context_pack_builder.py`

**Inputs:**
- `--source-sha256s <sha256_1> [sha256_2 ...]`
- `--request-type <str>` (implementation|test_generation|coverage_audit|review)
- `--index-version <int>`
- `--target-tokens <int>` (default: 4000)

**Outputs:**
- `context_pack_id` — printed to stdout
- Pack file: `.local/spec-artifacts/context-packs/{context_pack_id}.json`
- Pack includes: manifest_sha256, source_sha256s, verified requirements, sections, examples

**Validation:**
- manifest_sha256 computation verified by re-compute on load
- Stale check: all sources checked against vault before build
- Token count <= target_tokens

**Error handling:**
- Stale source: exit 2, STALE_SOURCE (name the stale sha256)
- Source not in vault: exit 1, SOURCE_NOT_IN_VAULT
- No verified requirements: exit 1, NO_VERIFIED_REQUIREMENTS

---

## Tool 11 — spec_governance_runtime

**Purpose:** Enforcement of ai-authority-boundary at all stream handoffs.
**Module:** `tools/specification-authority-layer/spec_governance_runtime.py`

**Inputs:**
- `--validate-handoff --stream <stream> --evidence <evidence_file>`
- `--check-staleness --context-pack-id <id>`
- `--scan-declaration --declaration <yaml_file>`

**Outputs:**
- ValidationResult: PASS | FAIL (reason) | WARN (caveat)
- JSON result to stdout

**Validation:**
- All four stream rules enforced (see four-stream-enforcement-model.md)
- Anti-bypass rules enforced

**Error handling:**
- Missing required field: FAIL with field name
- Stale pack: FAIL with stale_reason
- Unregistered source: FAIL with URL

---

## Tool 12 — coverage_validator

**Purpose:** Evaluate requirement coverage for a completed task.
**Module:** `tools/specification-authority-layer/coverage_validator.py`

**Inputs:**
- `--context-pack-id <id>` — the pack used for the task
- `--addressed-reqs <req_id_1> [req_id_2 ...]` — requirements addressed

**Outputs:**
- Coverage record written to usage ledger (type=coverage)
- JSON summary to stdout: coverage_ratio, addressed, missed

**Validation:**
- All addressed_reqs must be in the context pack's requirement_ids
- Coverage ratio = len(addressed) / len(total_in_pack)

**Error handling:**
- Pack not found: exit 1, CONTEXT_PACK_NOT_FOUND
- Requirement not in pack: exit 2, REQUIREMENT_NOT_IN_PACK (list each)

---

## Tool 13 — staleness_checker

**Purpose:** Check and propagate staleness for spec artifacts.
**Module:** `tools/specification-authority-layer/staleness_checker.py`

**Inputs:**
- `--check-source --source-id <id>` — check if source has changed
- `--propagate --source-sha256 <sha256>` — propagate staleness downstream
- `--report` — report all stale artifacts

**Outputs:**
- Check: `FRESH | STALE (new_sha256=...)` — printed to stdout
- Propagate: JSON list of stale artifact_ids
- Report: JSON table of all stale artifacts

**Validation:**
- Staleness check fetches current sha256 from source URL
- Propagation marks all downstream artifacts stale in metadata

**Error handling:**
- Source unreachable: exit 2, SOURCE_UNREACHABLE (cannot determine staleness; caveat)
- No downstream artifacts: exit 0 with INFO: NO_DOWNSTREAM_ARTIFACTS
