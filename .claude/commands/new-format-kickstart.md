---
version: "2.0"
last-updated: "2026-07-23"
phase-available: "3+"
gate-required: "Explicit product implementation authorization"
skill_type: "ROUTING_SKILL"
idempotency: "The same pinned ProductContract and input digests generate the same package chassis, obligation projection, checked-in generated source, and package artifacts."
loc_budget: "Production source is split by layer; no parser, writer, model, or generated module may become a multi-responsibility mega-file."
test_path: "tests/production_program/test_production_skills.py"
risk_level: "HIGH"
created-by: "TC-FF6-MACH-001"
product_track: "foss_python"
generated_by: codex
visibility: generated
---

# /new-format-kickstart

Create or migrate an independently publishable Python format library from a
compiled `ProductContract`. This is the production entry point for JSON,
binary, header-plus-payload, ZIP/container, schema-defined XML, and large
schema-generated families. A probe/load/write slice is an intermediate
checkpoint, never completion.

## Required Inputs

- `format_id`
- `distribution_name`
- `namespace` (must be `format_factory.<format_id>`)
- `family` (`json`, `binary`, `header_payload`, `zip_container`,
  `schema_xml`, or `large_schema_family`)
- `product_contract_path`
- `product_contract_sha256`
- `authority_digests`
- `release_profile`
- `source_root` (must resolve beneath `src/python/<format_id>/`)
- `test_root`
- `dependency_lock`
- `task_id`

## Routing

1. `json`: typed JSON model, schema/version validation, preservation, canonical
   serialization, differential oracle.
2. `binary`: bounded header decoder, checked arithmetic, lazy payload access,
   deterministic writer, official implementation oracle.
3. `header_payload`: raw header preservation plus normalized typed metadata,
   streaming/detached payload policy, decompression limits.
4. `zip_container`: central-directory and entry validation before extraction,
   path/duplicate/ratio limits, deterministic member order and timestamps.
5. `schema_xml`: namespace-aware secure XML, schema validation, extension
   preservation, canonical output, processing-requirement tests.
6. `large_schema_family`: deterministic schema compiler, stable collision
   rules, checked-in generated source, all-root inventory and regeneration
   proof.

## Execution

1. Run `/check-skill-coverage` and the Codex pre-mutation guard. Acquire a
   coordination lease for the exact product and test roots.
2. Load `KC-PYTHON-003`; refuse stale or missing knowledge.
3. Compile the ProductContract. Fail closed on missing/pending authority
   digests, foreign or unresolved SAL facts, or missing mandatory obligations.
4. Snapshot existing public behavior. If migrating an alpha package, add
   characterization tests and a symbol migration map before moving code.
5. Create a PEP 420 package. There is no `format_factory/__init__.py` and no
   top-level package that can collide with an upstream implementation.
6. Create `model/`, `codec/reader/`, `codec/writer/`, `validation/`,
   `security/`, `adapters/`, `analytics/`, and `cli/`. Models perform no I/O;
   analytics never enter codecs; optional dependencies remain in adapters.
7. Implement the common lifecycle API and format-specific obligations in
   deterministic, bounded task slices. Generated source is checked in with its
   generator and exact input digests.
8. Build wheel and sdist from a hash-locked environment. Verification imports
   only from the installed wheel in an empty working directory.
9. Bind every executed result to source, test, fixture, contract, authority,
   lock, tool, package, and environment digests in the canonical proof graph.
10. Compute promotion from live proof. Presence, prose deferrals, historical
    evidence, LLM output, and manual status edits never satisfy obligations.

## Mandatory Validations

- contract and referential integrity
- package namespace and architecture
- positive and rejection evidence for every MUST obligation
- semantic roundtrip and safe unknown-data preservation
- official and independent corpus/oracle evidence
- security/resource-limit, property, fuzz, mutation, typing, lint, and API checks
- installed-wheel tests on the supported Python matrix
- reproducible generation and two-build artifact equality
- SBOM, provenance, license, vulnerability, and extraction-boundary checks

## Allowed Paths

- `src/python/<format_id>/**`
- `tests/python/<format_id>/**`
- `shared/format-contracts/<format_id>.yaml`
- format-owned corpus, schemas, examples, docs, reports, and package manifests
- canonical proof and execution-manifest outputs

## Forbidden Paths

- `src/python/open-source/**`
- `src/dotnet/**`
- unrelated format roots
- `format_factory/__init__.py`
- top-level packages named `nrrd` or `safetensors`
- manual promotion fields
- mutable shared certification fixtures
- `plans/strategic/**`

## Stop Conditions

- Stop the affected obligation, not the program, if authority or proof closure
  is broken; create a current-state gap and continue another safe obligation.
- Do not install an undeclared dependency or weaken a validator to get green.
- Do not claim certification from source-tree imports, synthetic-only corpora,
  advisory checks, percentages, file presence, or self-review.
- After three materially different failed repairs for one root cause, mark that
  obligation technically blocked and continue other formats.

## Output

Emit a machine-readable execution manifest, changed-path list, input/output
digests, exact commands and exit codes, proof node IDs, current gaps, computed
promotion state, and the automatically selected next obligation.
