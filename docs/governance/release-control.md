# Release Control Policy

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run013: date updated; source path references verified consistent with format-first layout)
**Authority:** This document governs visibility classification and release decisions for all artifacts in format-factory.

---

## Purpose

This document defines how the format-factory project controls what becomes open source, what remains internal, what is commercial-only, and what is permanently blocked from publication. Every artifact produced in this project — source files, evidence documents, samples, schemas, generated outputs, LLM responses, and reports — must carry a visibility classification conforming to this policy from the moment it is created.

This policy applies to all contributors, human and agent alike. Agents must read and apply this document before creating any artifact.

---

## Visibility Classifications

Six visibility classes are recognized. Every artifact must be assigned exactly one class. When uncertain, default to `internal`. Never default to `public`.

### 1. `public`

The artifact is safe for open-source release. It was intentionally designed to be public. It carries a compatible open-source license. Its provenance (if required) is confirmed. It contains no commercial references, no PII, and no legally restricted content.

**Can be published:** Yes — in open-source releases after human review and release manifest approval.

### 2. `internal`

The artifact is a working document, plan, governance file, or taskcard intended for internal use only. It is not secret but is not designed for external audiences. It guides development but is not part of any product release.

**Can be published:** No. Internal artifacts may be made public individually with explicit human approval and visibility reclassification.

### 3. `commercial`

The artifact belongs to the commercial product track. It may reference commercial-tier features (Tier 5–6), proprietary configuration, or commercial licensing terms. It must never appear in any open-source release.

**Can be published:** Only in commercial releases, after Gate 11 and DD3 are resolved.

### 4. `evidence-only`

The artifact is acquisition evidence (spec analysis, legal notes, parser observations) that informs the product but is not itself released to users. It may contain quoted spec text with copyright implications, or other content that requires legal clearance before publication.

**Can be published:** No — remains internal evidence unless a specific release decision is made with legal review.

### 5. `generated`

The artifact was produced by an LLM or automated tool. It has not yet been reviewed and approved by a human for publication. It may contain hallucinations, inaccuracies, or content that requires verification.

**Can be published:** Conditionally — only after human review changes visibility to `public` or `internal`. An agent must never change visibility from `generated` to `public` without human approval.

### 6. `blocked`

The artifact is legally restricted, contains PII, was acquired without clear license, or has been explicitly prohibited from any publication by a rights holder, legal review, or project policy. This classification is permanent until a formal unblock decision is recorded in the gap register.

**Can be published:** Never, without a formal unblock process.

---

## Default Visibility by Artifact Type

| Artifact Type | Default Visibility | Notes |
|---|---|---|
| Plans, governance, architecture docs | `internal` | May be reclassified `public` explicitly |
| Registry (`format-registry.yaml`) | `internal` → `public` at Gate 9 | Reclassified when format reaches product mapping |
| Acquisition pack evidence | `evidence-only` | Remains evidence unless explicitly released |
| Cached spec files (`.local/spec-cache/`) | `evidence-only` | Local-only; never committed; `publish_allowed: false` |
| Cached spec metadata (spec-index.yaml) | `evidence-only` | Metadata may appear in evidence bundles without spec content |
| Samples (confirmed open-licensed) | `public` | Must have `provenance_status: confirmed` |
| Samples (uncertain license) | `blocked` | Remains blocked until license confirmed |
| Neutral model schemas | `internal` → `public` at Gate 10 | |
| Prototypes | `internal` | Never `public`; reference only |
| Python FOSS product (`src/python/{format}/`) | `public` | After Gate 10 |
| .NET product FOSS tiers (`src/net/{format}/`, if DEC-033 resolved) | `public` | After Gate 10 and DEC-033 resolved |
| .NET commercial tiers (`src/net/{format}/`) | `commercial` | After Gate 11 + DD3 resolved |
| LLM prompts and responses | `generated` or `evidence-only` | See LLM content rules below |
| Security reports | `internal` | May be partially reclassified `public` after redaction |
| Legal reports | `internal` | May be partially reclassified `public` after redaction |
| Release manifests | `public` | Generated at release time |
| `.env` secrets | `blocked` | Never committed |
| Agent run records | `internal` | Local-only; not committed |

---

## Open-Source Eligibility Rules

A file is open-source eligible if ALL of the following are true:

1. `visibility: public`
2. `publish_allowed: true`
3. `open_source_allowed: true`
4. `release_blockers` list is empty
5. License is compatible with the project's declared open-source license (Apache 2.0 or MIT, per `docs/product-tracks.md`)
6. `provenance_status: confirmed` (if `provenance_required: true`)
7. No commercial namespace, class, or configuration reference is present in the file

An agent must not mark a file as open-source eligible without verifying all seven conditions.

---

## Commercial Exclusion Rules

The following must never appear in any open-source release:

1. Files with `visibility: commercial`
2. Files with `commercial_allowed: true` and `open_source_allowed: false`
3. Any file containing commercial-tier source within `src/net/{format}/` (when implemented)
4. Any file containing a reference to a commercial namespace or commercial feature class
5. Any file with an unresolved entry in `release_blockers`

**Note:** `src/dotnet/commercial/` is an obsolete path and must not be created. Commercial-tier source lives within `src/net/{format}/`.

The CI boundary check (Phase 4+, per `docs/product-tracks.md`) enforces commercial exclusion automatically. Until CI exists, manual inspection is required at Gate 10.

---

## Cached Specification Release Rules

Specification documents downloaded to `.local/spec-cache/` are `evidence-only` with `publish_allowed: false`. The following rules apply:

1. **Cached spec files are never included in release manifests.** They are local-only evidence inputs, not release artifacts.
2. **Default `redistribution_permitted: false`.** Most standards body publications prohibit redistribution even when reading and implementing are freely permitted. See `docs/legal-and-licensing.md` for the four permissions distinction.
3. **Spec-index.yaml metadata** (source URL, version, SHA-256, download date, legal category, redistribution status) may be included in evidence bundles as citation metadata, without including the spec document content.
4. **Committing a spec document** requires confirmed redistribution permission plus explicit human approval documented in the gap register. This is exceptional and must be explicitly authorized.
5. **Spec citations in committed artifacts** must be minimal: cite the spec version, section reference, and source URL. Do not quote substantial spec text in committed files.

---

## LLM-Generated Content Rules

1. All LLM-generated content defaults to `visibility: generated`.
2. LLM content that quotes spec text defaults to `visibility: evidence-only` pending legal review.
3. An agent may never change visibility from `generated` to `public` without human approval.
4. LLM prompts and responses are stored locally only (`.local/llm-cache/`) and are never committed.
5. When LLM-generated content is incorporated into a committed artifact (e.g., an agent drafts a section of `spec-evidence.md`), the artifact's `generated_by` field must record the model used.
6. Committed artifacts containing LLM-generated content must be reviewed before their visibility can be upgraded from `generated` or `evidence-only` to `public`.

---

## Release Manifest

A release manifest is a YAML file listing every artifact included in a release, with its path, visibility, license, provenance status, and any release blockers. Release manifests are produced by the release manifest tool (TC-0006, Phase 3+). Until that tool exists, release manifests are created manually.

A release may not proceed without a human-reviewed release manifest. The manifest review confirms:
- No `commercial` artifacts are present in an open-source release.
- No `blocked` artifacts are present.
- No `generated` artifacts are present without explicit human approval.
- All samples have `provenance_status: confirmed`.
- All license fields are populated.

---

## Artifact Visibility Schema

All artifacts must carry front matter conforming to the following schema. This schema is used in artifact files, `artifact-index.yaml`, and release manifests.

```yaml
artifact_id: string          # Unique ID, e.g. "fods-spec-evidence-v1"
artifact_type: string        # plan|registry|taskcard|acquisition-pack|sample|schema|
                             # prototype|report-security|report-legal|release-manifest|
                             # source-python-foss|source-net-foss|source-net-commercial|
                             # llm-prompt|llm-response|run-record|tool-script
path: string                 # Relative path from repo root
format_id: string|null       # e.g. "fods", null for non-format artifacts
product_family: string|null  # cells|words|slides|imaging|diagram|archive|null
visibility: string           # public|internal|commercial|evidence-only|generated|blocked
publish_allowed: boolean     # Whether this can appear in any release
license: string|null         # SPDX identifier, null if not applicable
provenance_required: boolean # Whether a provenance record is required
provenance_status: string    # confirmed|unconfirmed|missing|not-applicable
source_hash: string|null     # sha256:<hash> of the primary source
generated_by: string|null    # "human"|"claude"|"codex"|"tool:<name>"|null
generated_at: string|null    # ISO-8601 datetime
reusable: boolean            # Whether agents can reuse without regenerating
refresh_policy:
  trigger: string            # source-changed|spec-version-changed|tool-version-changed|
                             # manual|age
  max_age_days: integer|null # null = no age-based staleness
stale: boolean               # true = refresh needed
open_source_allowed: boolean # Whether this can appear in open-source releases
commercial_allowed: boolean  # Whether this can appear in commercial releases
release_blockers: list       # Blocking issues; empty means no blockers
notes: string|null           # Human-readable notes
```

Front matter is required on all files in: `acquisition-packs/`, `samples/by-format/`, `reports/`, `schemas/neutral-model/`, `src/`. Front matter is validated by TC-0006 scope tooling before any gate is approved.

### Hybrid Classification Policy for Phase 0 Governance Files

Phase 0 governance and infrastructure files (docs, AGENTS.md, GOVERNANCE.md, ROADMAP.md, README.md, registry files, `_readme.md` files, `.gitignore`, `.env.example`, `.claude/settings.json`, `tools/llm/endpoints.yaml`, `plans/master-plan.md`) are classified via `.local/artifact-index.yaml` rather than inline front matter. This hybrid policy is applied because:

1. Configuration files (`.gitignore`, `.env.example`, `.claude/settings.json`, YAML config files) cannot carry Markdown front matter without breaking their syntax.
2. Top-level governance documents (AGENTS.md, GOVERNANCE.md, README.md) do not conventionally carry YAML front matter and are better classified centrally.
3. The artifact index in `.local/artifact-index.yaml` provides the same visibility classification for these files; it is bootstrapped in Phase 0 and maintained automatically from Phase 1 onwards.

**Rule:** For Phase 0 governance files classified via artifact-index.yaml, the file itself need not carry a front matter block. The artifact-index entry is authoritative for visibility classification purposes. For Phase 1+ acquisition artifacts (`acquisition-packs/<format-id>/`, `samples/by-format/`, `schemas/neutral-model/`, `src/`, `reports/`) front matter is mandatory directly in the file. Taskcards and acquisition pack templates may carry front matter (and the provided templates do).

---

## Boundary Testing Before Release

Before Gate 10 (open-source release) and Gate 11 (commercial release):

1. Run the open-source solution build in isolation to confirm zero commercial references.
2. Review the release manifest for `commercial`, `blocked`, and `generated` artifacts.
3. Verify all `provenance_required: true` samples have `provenance_status: confirmed`.
4. Confirm no LLM-generated content without human approval is in the release.
5. Record boundary check results in the gate approval note.

Until CI exists (Phase 4+), boundary testing is performed manually by the project lead.

---

## Rule Summary

> **Default to `internal` when uncertain. Never default to `public`.**

> **An agent must never upgrade visibility to `public` without human review.**

> **Commercial artifacts must never appear in open-source releases.**

> **Blocked artifacts must never be released without a formal unblock process.**
