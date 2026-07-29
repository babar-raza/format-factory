---
version: "1.0"
last-updated: "2026-07-29"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
idempotency: "create_or_update"
loc_budget: "authority lock/materializer + research plane; decomposition is mandatory"
test_path: "tests/format_contract/test_research_plane.py; tests/format_contract/test_authority_materializer.py"
risk_level: HIGH
created-by: TC-FCL-030
product_track: format_contract
generated_by: codex
visibility: generated
---

# /research-format-contract-sources

Research plane of the L30 Format Contract Layer: build source records, author
reviewed research findings, and commit them through the intake gate to
`shared/format-contracts/research/{format_id}.yaml`.

For formats enrolled in `shared/format-contracts/authority-lock.yaml`, this
skill is also the only acquisition path. The lock binds the primary locator,
permitted redirect hosts, byte/resource limits, legal-use disposition,
materialized path, and exact SHA-256. External bytes are never committed: they
live in the content-addressed `.local/format-contracts/authority-cas/` and
`.local/format-contracts/acquired/` roots. The checked-in lock and internal
product-requirement records are the reproducible declarations.

This is the ONLY channel through which non-normative knowledge (developer use
cases, API expectations, ecosystem practice) reaches contract compilation.
Normative claims are refused by the intake and routed to the SAL candidate
queue (`.local/supervisor/sal-candidates/{format_id}.yaml`) for L01-governed
commit via the ingest-spec-sal manual-seed path — this skill NEVER writes
`shared/sal-facts/`.

## Steps

1. Validate and audit the lock without network:
   `python -m tools.format_contract.authority_materializer audit --format <fmt>`.
   A missing artifact is a blocking result, not permission to relabel it.
2. For internal `PRODUCT_REQUIREMENT` records, run
   `python -m tools.format_contract.authority_materializer
   sync-product-requirements --format <fmt> --check`. Regeneration without
   `--check` is allowed only for the deterministic checked-in internal record.
3. Materialize enrolled sources:
   `python -m tools.format_contract.authority_materializer materialize
   --format <fmt>` for offline CAS replay; add `--online` only when network
   acquisition is explicitly authorized. Never fetch an enrolled source
   outside this command.
4. Require exact source and contract closure:
   `python -m tools.format_contract.authority_materializer audit
   --format <fmt> --contracts`. Every record must report `MATCH`.
5. Run `python tools/format_contract/source_researcher.py --format-id <fmt>`
   (`--allow-network` delegates only to the locked materializer) to build the
   source-record skeleton in `.local/format-contracts/drafts/`.
6. Author findings in `.local/format-contracts/drafts/{fmt}-draft.yaml`:
   every finding cites `source_ids`, states one testable requirement
   (>= 25 chars), and carries a `review` block
7. Review pass: set verdict ACCEPTED/REJECTED per finding (independent lane
   for pilot formats — /review-format-contract)
8. `python tools/format_contract/research_intake.py --format-id <fmt>` —
   validates (schema, source closure, normative-marker refusal, review gate)
   and commits ACCEPTED findings canonically

## Mandatory Validations

- **review_gate_enforced**: PENDING/REJECTED findings never commit
- **source_closure**: every finding's source_ids resolve to source records
- **normative_routing**: normative-sounding requirements refused with routing hint
- **no_sal_store_write**: `shared/sal-facts/` untouched
- **authority_lock_schema_valid**: duplicate IDs/paths, unsafe paths, invalid
  locators, incomplete legal records, and unbounded retrieval are rejected
- **authority_digest_exact**: only exact locked bytes can reach acquired paths
- **legal_use_approved**: `BLOCKED` legal status prevents all materialization
- **secure_bounded_fetch**: HTTPS, redirect/host, byte, timeout, ZIP member,
  decompression, and duplicate-target constraints fail closed
- **atomic_concurrent_materialization**: concurrent writers can publish only
  identical expected bytes; partial files never become authority
- **offline_cas_replay**: a populated CAS reconstructs acquired paths with no
  network access
- **contract_declaration_closure**: every locked source is declared exactly
  once by its format contract and every declaration resolves to the lock

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier |

## Allowed Paths

- `.local/format-contracts/authority-cas/**`,
  `.local/format-contracts/acquired/**`,
  `.local/format-contracts/drafts/**`,
  `.local/supervisor/sal-candidates/**` (write)
- `shared/format-contracts/authority-lock.yaml` (reviewed declaration)
- `shared/format-contracts/product-requirements/{format_id}.yaml`
  (deterministic internal authority only)
- `shared/format-contracts/research/{format_id}.yaml` (write via intake only)

## Forbidden Paths

- `shared/sal-facts/**` (L01 owns commits), `src/**`, `plans/from_chat/**` (DEC-038)

## Stop Conditions

- Lock/materialization/audit failure: repair the declaration, retrieval
  policy, legal disposition, or bytes; never downgrade or bypass.
- Intake REFUSED: repair the draft (sources/review/normative routing); never bypass.

## Output Format

Materialization/audit JSON with exact observed digests, committed-finding
count, queued SAL candidate count, and store path.

## Idempotency Contract

Re-running intake with the same draft rewrites the same canonical store
byte-identically; SAL queue rewritten from draft (no duplicates). Re-running
materialization from the same lock and CAS produces identical acquired bytes.
Three fresh strict contract/capability compilations must remain byte-identical.
