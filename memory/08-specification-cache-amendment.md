---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run012
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 08 — Specification Acquisition and Local Cache Amendment

## Requirement origin

The human clarified that the earlier “everything must be available on disk” rule also applies to standardized file-format specifications and related format materials.

This is now a first-class architecture requirement.

## Core rule

Any standardized file-format specification, public standard, schema, official reference material, public registry entry, or legally usable reference material that is available online must be:

1. acquired systematically
2. saved cleanly to local disk
3. indexed with provenance, version, source URL, license, redistribution status, and checksum
4. reused locally instead of repeatedly downloaded
5. refreshed only when source metadata or content proves it changed

## Default storage policy

Downloaded specs are local-only by default:

```text
.local/spec-cache/
```

`.local/spec-cache/` is gitignored.

The repo should commit:

- policies
- schemas
- metadata/index rules
- references
- taskcards

The repo should not commit downloaded specs unless redistribution is explicitly allowed and the human approves.

## Materials covered

The cache layer covers:

- OASIS specifications
- W3C specifications
- ECMA specifications
- ISO specs when legally accessible
- IETF RFCs
- official vendor specs
- PRONOM entries
- Library of Congress format descriptions
- IANA/MIME entries
- schemas such as XSD, DTD, RELAX NG
- official compatibility/version migration notes
- sample files only when license permits

## Metadata schema idea

Each cached item should eventually track:

```yaml
spec_id: string
title: string
format_id: string|null
product_family: string|null
source_type: official-standard|vendor-spec|registry-entry|schema|reference-doc|sample|other
publisher: string
source_url: string
canonical_url: string|null
version: string|null
date_published: string|null
date_accessed: string
license: string|null
redistribution_allowed: boolean
committed_to_repo: boolean
local_only: boolean
local_path: string
content_type: string|null
content_hash: sha256:<hash>
etag: string|null
last_modified: string|null
fetched_by: human|claude|codex|tool
fetched_at: string
refresh_policy:
  trigger: source-hash-changed|etag-changed|last-modified-changed|manual|age
  max_age_days: integer|null
stale: boolean
related_artifacts:
  - path
usage_notes: string|null
legal_notes: string|null
release_blockers:
  - string
```

## Gate 2 relationship

A format cannot pass Gate 2 without either:

1. cached spec/source metadata, or
2. an explicit “no official spec available” note.

Gate 2 evidence must cite cached metadata and original URLs.

## LLM relationship

Agents must not paste large copyrighted spec text into committed files or remote prompts.

LLM prompts should use:

- cached spec path
- short permitted excerpts
- metadata summaries
- section references

Full standards should not be sent to remote endpoints unless license, privacy, and human policy allow it.

Local LLMs may be preferred for private/local spec analysis, but endpoint use is not Phase 0.

## Phase status

Phase 0 added policy only:

- `docs/specification-cache.md`
- `tools/spec-cache/_readme.md`
- `taskcards/TC-0007-specification-cache.md`

No specs were downloaded in Phase 0.

## Phase 1/2 implementation (run019)

TC-0007 implemented in run019 (2026-05-04). Three scripts in `tools/spec-cache/`:

- `spec_index.py` — library: read/write/validate spec-index.yaml, compute SHA-256, staleness check
- `acquire_spec.py` — download + hash + index; dry-run by default; `--allow-network` required for live download; legal metadata required
- `refresh_check.py` — scan/validate/show; no auto-download

Status: `completed_pending_independent_verification`. Spec not downloaded (T3 not authorized in run019). No spec-index.yaml entries exist in `.local/spec-cache/`.

Implementation is Phase 1 via TC-0007.

## run009 authorization model amendment

run009 hardened the spec-cache policy with an explicit authorization model. This was not part of the original run008 design.

**Authorization model (confirmed run009):**

- Spec downloads require explicit prompt authorization before any fetch occurs.
- Agents must never self-authorize a download, even if a spec is missing or stale.
- If a spec is missing: stop, log a gap in the Gap Register, create a taskcard if needed, and wait for human authorization.
- If a spec is stale: stop, log the staleness, and wait for explicit authorization to refresh.
- This is called the **stop-log-gap model**.

**TC-0007 scope correction (run009):**

- TC-0007 originally scoped to FODS specifically.
- run009 corrected TC-0007 to be format-generic tooling that applies to all formats.
- The spec-cache layer exists before any format is selected; it is not tied to FODS.

**Effect on AGENTS.md:**

- Section T (Specification Cache Rules, formerly Section S) was updated in run010 to reflect the authorization model.
- T3-gap rule: agents must log a gap and stop if specs are missing, not self-fetch.
- T9 and T10 cross-references updated to refer to T3 authorization conditions.

**No specs downloaded as of run012.** Phase 0 boundary intact.
