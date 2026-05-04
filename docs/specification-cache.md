# Specification Cache Policy

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: global audit — content verified consistent with current governance)
**Authority:** This document governs the systematic local acquisition, storage, indexing, and reuse of standardized file-format specifications and official public materials used by the format-factory acquisition pipeline.

---

## Purpose

The format-factory project requires format specifications to be available on disk for reliable, reproducible, and audit-friendly acquisition work. Repeated downloads of the same specification document are wasteful, introduce version-drift risk, and may produce unreproducible results if the source changes. This document defines the specification acquisition and local cache layer: a systematic policy for downloading specs once, storing them locally, indexing them with provenance metadata, and reusing them across all acquisition phases.

This policy applies to all agents and human contributors. No spec-dependent acquisition work (evidence drafting, prototype development, oracle comparison) may begin without a cached and indexed copy of the relevant specification.

---

## Scope

The specification cache covers any standardized or official public material that governs format interpretation:

- **Primary specifications:** Official standards body publications (OASIS ODF, ECMA OOXML, W3C SVG, IETF RFCs, ISO documents, IEEE standards).
- **Secondary reference documents:** Errata, change logs, related schema files (.xsd, .rng, .dtd), official interoperability reports, and official test suites.
- **Registry metadata:** Format registry files published by standards bodies (IANA media type registry, PRONOM format signatures, library of congress format descriptions).
- **Official corrigenda and amendments:** Version-specific corrections published by the standards body after the base spec was released.

The cache does NOT include:
- Internal project artifacts (acquisition pack evidence, scoring sheets, reports).
- Third-party commentary, blog posts, or unofficial analyses (these are evidence-only and do not go in the spec cache).
- Samples (these go in `samples/by-format/` per `samples/_policy.md`).
- LLM-generated content (this goes in `.local/llm-cache/`).

---

## Storage Location

All cached specification files are stored at:

```
.local/spec-cache/
  <format-id>/
    <version>/
      spec.pdf              (or spec.html, spec.xml, etc.)
      spec-index.yaml       (provenance and metadata for this version)
      errata/               (errata documents, if any)
      schemas/              (normative schema files, e.g. .xsd or .rng, if part of the spec)
```

`.local/spec-cache/` is gitignored. It is local-only. Specification files are never committed to git because:

1. Specification documents may be large (multi-megabyte PDFs).
2. Copyright restrictions may prohibit redistribution (even if reading is permitted).
3. The spec-index.yaml provides the metadata needed to re-acquire any cached file from its canonical source URL when explicitly authorized.

Losing `.local/spec-cache/` does not permanently block work, but it does NOT automatically authorize re-download. If the cache is empty or stale, the agent must stop, log the missing-spec condition, and proceed with re-acquisition only if the current taskcard and execution prompt explicitly authorize it. See the Authorization Model section below.

---

## Spec Index Schema

Every acquired specification version is indexed at `.local/spec-cache/<format-id>/<version>/spec-index.yaml`. The schema is:

```yaml
spec_cache_entry:
  # --- Always required ---
  format_id: string              # e.g. "fods"
  spec_name: string              # e.g. "ODF 1.3 Part 3 — Open Document Schema"
  version: string                # e.g. "1.3"
  source_url: string             # URL where file was downloaded from
  canonical_url: string          # Official canonical URL for this spec version
  publisher: string              # Standards body name, e.g. "OASIS"
  legal_category: integer        # 1-4 per docs/legal-and-licensing.md
  license: string|null           # SPDX or descriptive (e.g. "OASIS RF on Limited Terms")
  redistribution_permitted: boolean  # Whether this file may be redistributed to third parties.
                                 # false is the correct default for local-only caching of most
                                 # standards-body documents. false does NOT block acquisition.
                                 # Only warn if redistribution is actually attempted.
  local_only: boolean            # Always true — spec files are never committed to git
  stale: boolean                 # true if source may have changed since download

  # --- Identity metadata (optional, recommended) ---
  spec_id: string|null           # Unique ID for this cache entry, e.g. "fods-odf13-part3"
  source_type: string|null       # official-standard|vendor-spec|registry-entry|schema|reference-doc|sample|other
  date_published: string|null    # ISO-8601 date the spec was published by the standards body
  date_accessed: string|null     # ISO-8601 date this URL was last accessed

  # --- Post-download fields (null until file is downloaded) ---
  download_date: string|null     # ISO-8601 date of download
  local_path: string|null        # Path relative to .local/spec-cache/ (alias for file_path)
  file_path: string|null         # Relative path within this version directory
  file_size_bytes: integer|null  # File size at download time (bytes)
  sha256: string|null            # "sha256:<hex>" digest of the downloaded file
  content_hash: string|null      # "sha256:<hex>" content hash (same as sha256 for downloads)
  mime_type: string|null         # e.g. "application/pdf" or "text/html"
  fetched_at: string|null        # ISO-8601 datetime of download
  fetched_by: string|null        # human|claude|codex|tool:<name>

  # --- Refresh and HTTP metadata ---
  last_verified: string|null     # ISO-8601 date of last staleness check
  etag: string|null              # HTTP ETag from last fetch (for conditional refresh)
  last_modified: string|null     # HTTP Last-Modified header from last fetch
  refresh_policy:
    trigger: source-hash-changed|etag-changed|last-modified-changed|manual|age
    max_age_days: integer|null

  # --- Release control ---
  release_blockers: []           # List of blocking issues; empty means no blockers
  notes: string|null             # Any relevant notes about this specific download
```

Agents must write a `spec-index.yaml` entry for every file acquired into the cache. Entries without a `spec-index.yaml` are untracked and treated as stale.

**On `redistribution_permitted`:** This field records whether the spec document may be redistributed to third parties. `redistribution_permitted: false` is correct and expected for most standards-body documents (OASIS, W3C, ECMA) that permit implementation but not redistribution of the document itself. `false` does NOT block local-only caching under `.local/spec-cache/`. It only blocks committing the spec file to git or distributing it externally. Do not treat `false` as suspicious or erroneous for local-only cache entries.

---

## Acquisition Rules

### Rule 1: Check Before Download

Before downloading any specification file, an agent must check `.local/spec-cache/<format-id>/<version>/` for an existing entry. If the file exists and `stale: false` in `spec-index.yaml`, reuse the cached file. Do not re-download.

### Rule 2: Staleness Definition

A cached spec is stale if any of the following is true:
1. `stale: true` is set in `spec-index.yaml`.
2. The standards body has published a new version of the spec since `download_date`.
3. `last_verified` is more than 90 days ago (trigger re-check of the source URL, not necessarily re-download).
4. The file SHA-256 computed from disk does not match the `sha256` in `spec-index.yaml` (file corrupted or modified).

A re-check confirms whether the source URL still serves the same content. A re-check may update `last_verified` and clear `stale` if the content is unchanged. If the content has changed, the entry is marked `stale: true` and a gap is logged. **Re-download after a staleness detection requires the same authorization as an initial download (see Authorization Model below).** Staleness detection does not automatically authorize re-download.

### Rule 3: Legal Classification Before Acquisition

Before acquiring any specification file, confirm the format's legal category (see `docs/legal-and-licensing.md`). Only specifications in Legal Categories 1-3 may be cached. Legal Category 5 or 6 formats may not enter the cache.

Set `redistribution_permitted: true` only if the standards body's publication terms explicitly permit redistribution. For most OASIS, W3C, and ECMA standards, the document is publicly accessible but redistribution restrictions may apply. When uncertain, set `redistribution_permitted: false` and note the concern in the `notes` field.

### Rule 4: Single Canonical Source

Each specification version must have exactly one canonical source URL. The canonical source is:
- The standards body's official download page (preferred).
- A stable archival URL (e.g., IETF datatracker for RFCs) if the primary download page is not stable.
- Never: third-party mirrors, CDNs, or unofficial hosting.

If the canonical URL becomes unavailable, log a gap and attempt to find the new canonical URL before re-acquiring. Do not substitute a third-party source without logging a gap and flagging for human review.

### Rule 5: Multi-Part Specifications

When a specification is published in multiple parts (e.g., ODF 1.3 Part 1: Packages, Part 2: Recalculated Formula, Part 3: Packages, Part 4: Formula), each part is a separate cache entry with its own `spec-index.yaml`. The top-level `<version>/` directory may contain multiple files. A `spec-index.yaml` listing all parts is required.

### Rule 6: Schema Files Are Part of the Spec

Normative schema files (XSD, RNG, DTD, JSON Schema) that are published as part of the official specification are acquired with the specification and stored in the `schemas/` subdirectory of the version directory. They are indexed in the same `spec-index.yaml` as separate entries under a `schemas:` list.

---

## Usage in Acquisition Pipeline

Specification cache files are inputs to multiple acquisition pipeline stages:

| Stage | How Spec Cache Is Used |
|---|---|
| Stage 1: Scoring | Spec metadata (legal category, completeness) informs Factor 1 and Factor 2 scoring; spec identification only — no download |
| Stage 2: Evidence Gathering | `spec-evidence.md` cites the cached spec version and records its SHA-256 |
| Stage 4: Prototype Development | Prototype reads parsing rules from the cached spec document |
| Stage 5: Neutral Model | Neutral model schema is designed against the cached spec's type system |
| Stage 6: Oracle Comparison | Discrepancies between prototype and oracle are verified against the cached spec |
| Stage 8: Security Review | Threat model is grounded in the cached spec's documented edge cases |

**Stage 1 (Scoring):** Stage 1 may identify which specification is relevant and confirm its legal category, but does not download the spec. The spec URL is recorded for future use.

**Stage 2 (Evidence Gathering):** Gate 2 evidence drafting proceeds in two phases:

1. **Draft phase (from recorded URLs):** An agent may begin drafting `spec-evidence.md` from officially recorded source URLs without a cached spec. Claims must be classified per the source-claim protocol: `[SUPPORTED_BY_RECORDED_URL]` for URL-backed claims, `[PLAUSIBLE_PENDING_VERIFICATION]` for technically sound but unverified claims. Draft evidence is marked `evidence_draft_pending_independent_verification`.

2. **Cache-backed phase (after authorized download):** After spec acquisition is authorized and completed, claims should be upgraded to `[SUPPORTED_BY_CACHED_SOURCE]` where the cached source supports them. Gate 2 evidence that includes cached-source claims is marked `evidence_cached_pending_independent_verification`.

**Gate 2 cannot pass until:** Either (a) cached-source-backed evidence exists, or (b) an explicit documented rationale for why no official spec can be cached is recorded in `spec-evidence.md`. A draft based on recorded URLs alone is not sufficient for Gate 2 passage without human review and sign-off.

**If the cache is missing:** The agent may draft from recorded URLs (draft phase above). The agent must NOT self-authorize a download. If download is needed to complete Gate 2 evidence, log the missing-spec condition as a gap and proceed only if the current execution prompt explicitly authorizes acquisition. If acquisition is not authorized, create or update a taskcard for spec acquisition.

**Missing cache is not automatic authorization to download.** See the Authorization Model section below.

---

## Refresh Policy

The specification cache may be refreshed on the following triggers. **Refresh checks may detect staleness and log gaps but must NOT automatically re-download spec content.** Re-download requires the same authorization as an initial download (see Authorization Model below).

1. **New version published:** When the standards body publishes a new version of the spec, the new version may be acquired as a new `<version>/` subdirectory after authorization. The old version is retained (historical reference). A gap or taskcard must be logged when a new version is detected, not an automatic download.
2. **Staleness detected:** When `stale: true` or `last_verified` is more than 90 days old, the agent runs a re-check of the source URL metadata. If content has changed, the entry is marked `stale: true` and a gap is logged. Re-download is not automatic.
3. **Hash mismatch:** If the SHA-256 of the file on disk does not match `spec-index.yaml`, the entry is marked `stale: true` and a gap is logged. The file must be re-acquired only with explicit authorization.
4. **Explicit refresh request:** A human or agent may set `stale: true` to flag an entry for re-acquisition. Actual re-download requires a subsequent authorized execution prompt.
5. **Monthly refresh scan:** During the monthly refresh process described in `docs/acquisition-workflow.md`, spec cache entries are verified for staleness. The scan sets `stale: true` where warranted and creates refresh taskcards; it does not automatically re-download.

Old versions are never automatically deleted. Deletion requires explicit human decision and is recorded in the gap register.

---

## Authorization Model for Spec Acquisition

Spec acquisition is not automatic. Every download requires explicit authorization. This section defines the authorization conditions that must ALL be satisfied before any spec file is downloaded.

### Required Authorization Conditions

1. **Correct phase:** Spec acquisition is Phase 1+. Phase 0 prohibits all downloads.
2. **Explicit taskcard:** A taskcard must exist that covers spec acquisition for the specific format and version. TC-0007 covers generic tooling only; it does not authorize any real download. Format-specific acquisition must be covered by a separate taskcard (e.g., a Phase 1/2 task for FODS spec acquisition).
3. **Legal category confirmed:** The format's legal category must have been reviewed and confirmed as Category 1, 2, or 3 before acquisition begins. Category 5 or 6 is an automatic block.
4. **Canonical source URL approved:** The canonical source URL (standards body official page or stable archival URL) must be identified and approved. No mirrors. No unofficial sources.
5. **Explicit execution prompt authorization:** The current execution prompt must explicitly state that spec acquisition is authorized for this format, name the format, version, and canonical URL, and state that storage under `.local/spec-cache/` is the intended destination.
6. **Local-only storage confirmed:** The acquired spec will be stored under `.local/spec-cache/` (gitignored, never committed). Redistribution rights must be assessed and recorded in `spec-index.yaml`.

### If Authorization Is Not Present

If any authorization condition is not satisfied, the agent must:
1. Stop before attempting any download.
2. Log a gap noting that a required spec is missing and acquisition is not authorized.
3. Create or update a taskcard for spec acquisition with the required authorization conditions to be resolved.
4. Continue other work that does not depend on the missing spec, or stop if all remaining work depends on the spec.

### Committed Copies of Specs

Committing a downloaded spec to git is prohibited by default. Committing requires:
1. Explicit human approval documented in the gap register.
2. Confirmed redistribution permission from the standards body (not just permission to read).
3. A visibility classification of `public` (requiring the redistribution permission above).

For most standards body publications, redistribution is not permitted even when reading is freely allowed. Default `redistribution_permitted: false`.

---

## Visibility and Confidentiality

Cached specification files are `visibility: evidence-only`. They are local-only and never committed. The spec-index.yaml entries (without the file content) may be included in evidence bundles as metadata, but the specification files themselves must not appear in any bundle.

If a specification document contains content with copyright restrictions that may affect how it is handled:
- Note this in the `notes` field of `spec-index.yaml`.
- Set `redistribution_permitted: false`.
- Do not quote substantial spec text in committed artifacts (applies to LLM prompts and evidence docs — see `docs/llm-endpoint-strategy.md`).

---

## Implementation

The specification cache tooling was implemented in Phase 1 (run019) via TC-0007:

| Component | Phase | Path | Description | Status |
|---|---|---|---|---|
| Cache policy (this doc) | Phase 0 | `docs/specification-cache.md` | Policy and schema | Complete |
| Cache directory orientation | Phase 0 | `tools/spec-cache/_readme.md` | Directory orientation file | Complete |
| Cache implementation taskcard | Phase 0 | `taskcards/TC-0007-specification-cache.md` | Phase 1 implementation scope | completed_pending_independent_verification |
| Index library | Phase 1 | `tools/spec-cache/spec_index.py` | Read/write/validate spec-index.yaml | Implemented run019 |
| Acquisition script | Phase 1 | `tools/spec-cache/acquire_spec.py` | Download, hash, index; dry-run default; --allow-network for live download | Implemented run019 |
| Refresh script | Phase 1 | `tools/spec-cache/refresh_check.py` | Staleness checking; never downloads | Implemented run019 |

**As of run020:** All three scripts are implemented, committed, and smoke-tested. No spec files have been downloaded yet. FODS/ODF spec acquisition is authorized in run020 (see TC-0009 and run020 execution prompt).

---

## Relationship to Other Documents

- `docs/acquisition-workflow.md` — Stage 2 requires a cached spec before `spec-evidence.md` is drafted
- `docs/legal-and-licensing.md` — legal category governs which specs may be cached
- `docs/release-control.md` — cached specs are `visibility: evidence-only`, never released
- `AGENTS.md` Section S — spec-cache acquisition rules for agents
- `taskcards/TC-0007-specification-cache.md` — Phase 1 implementation scope
- `tools/spec-cache/_readme.md` — directory orientation
