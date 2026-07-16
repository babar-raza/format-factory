---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
idempotency: "create_or_update"
loc_budget: "tools/format_contract/source_researcher.py + research_intake.py (~230 lines combined)"
test_path: "tests/format_contract/test_research_plane.py"
risk_level: MEDIUM
created-by: TC-FCL-030
product_track: format_contract
---

# /research-format-contract-sources

Research plane of the L30 Format Contract Layer: build source records, author
reviewed research findings, and commit them through the intake gate to
`shared/format-contracts/research/{format_id}.yaml`.

This is the ONLY channel through which non-normative knowledge (developer use
cases, API expectations, ecosystem practice) reaches contract compilation.
Normative claims are refused by the intake and routed to the SAL candidate
queue (`.local/supervisor/sal-candidates/{format_id}.yaml`) for L01-governed
commit via the ingest-spec-sal manual-seed path — this skill NEVER writes
`shared/sal-facts/`.

## Steps

1. `python tools/format_contract/source_researcher.py --format-id <fmt>`
   (add `--allow-network` only with explicit authorization) — builds the
   source-record skeleton in `.local/format-contracts/drafts/`
2. Author findings in `.local/format-contracts/drafts/{fmt}-draft.yaml`:
   every finding cites `source_ids`, states one testable requirement
   (>= 25 chars), and carries a `review` block
3. Review pass: set verdict ACCEPTED/REJECTED per finding (independent lane
   for pilot formats — /review-format-contract)
4. `python tools/format_contract/research_intake.py --format-id <fmt>` —
   validates (schema, source closure, normative-marker refusal, review gate)
   and commits ACCEPTED findings canonically

## Mandatory Validations

- **review_gate_enforced**: PENDING/REJECTED findings never commit
- **source_closure**: every finding's source_ids resolve to source records
- **normative_routing**: normative-sounding requirements refused with routing hint
- **no_sal_store_write**: `shared/sal-facts/` untouched

## Required Inputs

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier |

## Allowed Paths

- `.local/format-contracts/drafts/**`, `.local/supervisor/sal-candidates/**` (write)
- `shared/format-contracts/research/{format_id}.yaml` (write via intake only)

## Forbidden Paths

- `shared/sal-facts/**` (L01 owns commits), `src/**`, `plans/from_chat/**` (DEC-038)

## Stop Conditions

- Intake REFUSED: repair the draft (sources/review/normative routing); never bypass

## Output Format

Committed-finding count, queued SAL candidate count, store path.

## Idempotency Contract

Re-running intake with the same draft rewrites the same canonical store
byte-identically; SAL queue rewritten from draft (no duplicates).
