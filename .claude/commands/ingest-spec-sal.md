---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LA-004
spec_qname_required: "false"
product_track: "sal_ingestion"
---

# /ingest-spec-sal

Ingest a format specification into the SAL (Specification Authority Layer) to produce
`FACT-{FORMAT}-NNN` entries in `sal-facts-latest.json`.

This skill is the ONLY governed entry point for adding spec facts. Do NOT manually
edit `sal-facts-latest.json` or `.local/spec-cache/` files.

## Prerequisites (ALL required before execution)

1. **Spec source MUST exist** — a PDF, HTML, or plain-text specification for the format
   must be available at a stable URI or locally in `.local/spec-cache/`.
2. **Format must have a qname-registry entry** — `shared/qname-registry/{format}.yaml`
   must exist with at least one entry in `implementing` or `implemented` status.
3. **Format ID must appear in gap-ledger** — at least one `GAP-CHAIN-{FORMAT}-SAL-*`
   entry must exist in `reports/capability-layer/gap-ledger.json`.

## Mandatory Validations (run before declaring success)

- **sal_facts_nonzero**: After ingestion, `sal-facts-latest.json` must contain ≥1
  spec_fact for the target format. Zero facts = ingestion failed.
- **spec_fact_refs_populated**: Each extracted fact must have a non-empty `qname`
  field matching pattern `^FACT-{FORMAT}-[0-9]+$` and a non-empty `claim` field.
- **schema_valid**: The updated `sal-facts-latest.json` must validate against
  `schemas/sal-facts/sal-facts-schema.json`.

## Handoff Fields (required in execution context)

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier (e.g. `csv`, `tsv`, `gnumeric`) |
| `spec_source_uri` | URI or local path to the specification document |
| `spec_version` | Version of the specification (e.g. `RFC 4180`, `ODF 1.3`) |
| `spec_body` | Issuing body (e.g. `IETF`, `OASIS`, `LibreOffice`) |
| `target_fact_count_min` | Minimum expected fact count after ingestion (for validation) |

## Execution Steps

1. Verify prerequisites — check qname-registry entry and gap-ledger entry exist
2. Run the SAL extractor:
   ```
   python tools/spec/extract_sal_facts.py \
     --format-id <format_id> \
     --spec-source <spec_source_uri> \
     --output .local/sal-output/sal-facts-<format_id>.json
   ```
3. Merge into the combined database:
   ```
   python tools/spec/merge_sal_facts.py \
     --input .local/sal-output/sal-facts-<format_id>.json \
     --into .local/spec-cache/sal-facts-latest.json
   ```
4. Validate the result:
   ```
   python -c "
   import json, jsonschema, pathlib
   schema = json.loads(pathlib.Path('schemas/sal-facts/sal-facts-schema.json').read_text())
   data = json.loads(pathlib.Path('.local/spec-cache/sal-facts-latest.json').read_text())
   jsonschema.validate(data, schema)
   print('SCHEMA VALID')
   "
   ```
5. Confirm `sal_facts_nonzero` — count facts for target format in the merged file
6. Close the `GAP-CHAIN-{FORMAT}-SAL-*` entry in gap-ledger if all facts extracted

## Evidence Artifacts Required

- `.local/sal-output/sal-facts-<format_id>.json` — raw extracted facts
- A grep/count showing ≥1 fact for the format in `sal-facts-latest.json`
- Schema validation output (SCHEMA VALID)
- Gap-ledger closure record

## Known Gaps (as of 2026-06-26)

The following 14 formats have zero spec_facts and are candidates for this skill:
`csv`, `tsv`, `ndjson`, `abw`, `dif`, `gnumeric`, `sylk`, `toml`, `xcf`, `zst`,
`pbm`, `pgm`, `ppm`, `qoi`

SAL extraction tools may not yet support all spec formats. For stdlib-backed formats
(CSV, TSV, NDJSON, ZST), see `/run-oracle` for an alternative approach using Python
reference implementations.

## Required Inputs

- `format_id` — format identifier from the format registry
- `spec_source_uri` — value for `spec_source_uri`
- `spec_version` — value for `spec_version`
- `spec_body` — value for `spec_body`
- `target_fact_count_min` — value for `target_fact_count_min`

## Allowed Paths

- `tools/spec/extract_sal_facts.py`
- `tools/spec/merge_sal_facts.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/**` — no product source mutation during SAL ingestion
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid
