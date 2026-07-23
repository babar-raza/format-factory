---
version: "2.0"
last-updated: "2026-07-23"
phase-available: "all"
gate-required: null
created-by: TC-LA-004
spec_qname_required: "false"
product_track: "sal_ingestion"
---

# /ingest-spec-sal

Ingest a format specification into the SAL (Specification Authority Layer) to
produce canonical `SAL-{FORMAT}-<stable-id>` facts and derived
`FACT-{FORMAT}-NNN` compatibility aliases.

This skill is the only governed entry point for adding specification facts.
Do not manually edit the combined cache in `.local/spec-cache/`.

## Prerequisites

1. The specification source is acquired and digest-pinned. A PDF, HTML,
   schema, archive, or plain-text specification appears as an `ACQUIRED`
   source record with a SHA-256 `content_hash` in
   `shared/format-contracts/research/{format}.yaml`.
2. Every reviewed candidate cites acquired `source_ids`. An optional
   `source_sha256` declaration must match the acquired record.
3. QName registries are downstream. A format may initialize SAL before a
   QName registry or product source exists; requiring them here creates a
   circular dependency.
4. The active authority gap is recorded in the historical gap ledger or the
   production controller's current-gap projection. A missing legacy
   `GAP-CHAIN-*` row never authorizes unpinned ingestion.

## Mandatory validations

- `sal_facts_nonzero`: the target format contributes at least one fact.
- `spec_fact_refs_populated`: every fact has a canonical SAL ID, a non-empty
  `FACT-{FORMAT}-NNN` alias, and a non-empty claim.
- `authority_digest_bound`: every newly committed fact records acquired source
  IDs and SHA-256 digests.
- `schema_valid`: the derived combined database validates against
  `schemas/sal-facts/sal-facts-schema.json`.
- `strict_contract_resolves`: the strict ProductContract resolves all new fact
  references.

## Required inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase canonical registry identifier |
| `spec_source_uri` | Acquired URI or local authority path |
| `spec_version` | Pinned specification version/profile |
| `spec_body` | Issuing authority |
| `target_fact_count_min` | Minimum expected facts after ingestion |

## Execution

1. Verify acquired source records and SHA-256 digests.
2. Run the SAL extractor when the authority type has a supported extractor:

   ```text
   python tools/spec/extract_sal_facts.py \
     --format-id <format_id> \
     --spec-source <spec_source_uri> \
     --output .local/sal-output/sal-facts-<format_id>.json
   ```

3. For reviewed candidates from the research plane, commit through the
   authority-bound manual-seed path:

   ```text
   python tools/spec/seed_sal_candidates.py \
     --format-id <format_id> \
     --added-by <task_id>
   ```

   The seeder initializes a missing canonical store, preserves existing facts
   by union, verifies source digests, and records authority evidence in fact
   provenance.
4. Rebuild the derived combined database:

   ```text
   python tools/spec/merge_sal_facts.py
   ```

5. Validate the combined database against
   `schemas/sal-facts/sal-facts-schema.json`.
6. Confirm the target fact count meets `target_fact_count_min`.
7. Compile the strict ProductContract and prove every referenced fact resolves.
   Close the authority gap only when all checks pass.

## Evidence artifacts

- Acquired source record and SHA-256 digest.
- Reviewed candidate queue.
- Canonical `shared/sal-facts/{format_id}.yaml`.
- Derived combined-cache validation output.
- Strict ProductContract result.
- Skill transcript with exact inputs, commands, and digests.

## Allowed paths

- `tools/spec/extract_sal_facts.py`
- `tools/spec/merge_sal_facts.py`
- `tools/spec/seed_sal_candidates.py`
- `shared/sal-facts/{format_id}.yaml` — seeder-only append/initialization
- `.local/sal-output/**`
- `.local/spec-cache/**`
- `reports/**`

- `schemas/sal-facts/sal-facts-schema.json` â€” versioned ingestion schema

## Forbidden paths

- `src/**`
- `plans/strategic/**`
- manual edits to the combined SAL cache
- facts without acquired authority digests

## Stop conditions

- Stop the affected format if an authority digest is missing or mismatched.
- Stop if the canonical store or combined cache fails schema/identity checks.
- Do not manufacture a QName or product implementation to satisfy ingestion.
