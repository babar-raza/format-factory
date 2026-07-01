# Sample Policy

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-03
**Authority:** This document governs the acquisition, licensing, and storage of all sample files in the `samples/` directory.

---

## Purpose

Sample files are the raw material for prototype development, oracle comparison, fuzz testing, and product test suites. Every sample in this repository must have a confirmed, compatible open-source license. Samples acquired without license confirmation are blocked from use until confirmed. This policy applies to every file in `samples/by-format/` and every entry in `samples/_provenance.yaml`.

---

## Acceptable Licenses

Samples may only be committed if they carry one of the following licenses:

| License | Attribution Required? | Share-Alike Required? | Modification Allowed? | Commercial Use Allowed? |
|---|---|---|---|---|
| Creative Commons Zero (CC0) | No | No | Yes | Yes |
| Public Domain (explicit dedication) | No | No | Yes | Yes |
| Creative Commons Attribution (CC-BY) | Yes | No | Yes | Yes |
| Creative Commons Attribution-ShareAlike (CC-BY-SA) | Yes | Yes | Yes | Yes |
| Apache 2.0 | Yes | No | Yes | Yes |
| MIT | Yes | No | Yes | Yes |
| Project-created (owned by project) | N/A | N/A | Yes | Yes |

## Prohibited Licenses

The following licenses are NOT acceptable:

| License | Reason |
|---|---|
| CC-BY-ND (No Derivatives) | Prevents modification for test variants |
| CC-BY-NC (Non-Commercial) | Incompatible with commercial product testing |
| CC-BY-NC-SA | Both NC and SA restrictions |
| CC-BY-NC-ND | Both NC and ND restrictions |
| Unknown / Unconfirmed | Cannot confirm compatibility |
| Commercially licensed software output | Blocked regardless of incidental access |
| All-rights-reserved content | Cannot be used without explicit permission |

---

## Provenance Requirement

Every sample file must have a corresponding entry in `samples/_provenance.yaml` with `provenance_status: confirmed` before the file may be committed. Entries with `provenance_status: unconfirmed` are blocking: they prevent Gate 3 from passing.

If a sample's license cannot be confirmed, its `visibility` must be set to `blocked` and the file must not be used in any test, oracle comparison, or product.

---

## Sample Creation

When no adequately licensed sample is available for a required sample type, the project may create original samples. Original samples:
- Are owned by the project.
- May be licensed Apache 2.0 or CC0 at the project lead's discretion.
- Must be minimal — the smallest file that exercises the target feature set.
- Must be documented in `_provenance.yaml` with `source: project-created`.
- Must not be derived from or inspired by commercially licensed file content.

---

## Storage Location

Samples are stored at `samples/by-format/<format-id>/`. Each format has its own subdirectory. File names must be descriptive: `minimal.fods`, `empty.fods`, `core-data.fods`, `edge-case-empty-rows.fods`. Names must not include version numbers unless multiple versions of the same file are intentionally kept.

---

## Attribution Requirements

For CC-BY and CC-BY-SA samples, attribution must be recorded in `samples/_provenance.yaml`. Attribution must include:
- Creator name or organization
- Source URL
- License URL
- Date accessed

Attribution is surfaced in product documentation and test runner output. Automated attribution generation is deferred to Phase 4+ tooling.

---

## Sample Refresh Policy

Samples are acquired artifacts. They are not periodically regenerated. They should be refreshed only when:
1. The source has been updated and the new version is materially different.
2. A bug in the sample is discovered (the sample does not conform to the spec).
3. A fuzz-generated crash reveals that the sample exercises a dangerous pattern in the parser.

Sample refresh creates a new file with a version suffix or replaces the original with an updated provenance entry.

---

## Relationship to Other Documents

- `samples/_provenance.yaml` — per-sample license records
- `docs/governance/legal-and-licensing.md` — acceptable license list and provenance policy
- `docs/gates.md` — Gate 3 requires all samples to have confirmed provenance
- `acquisition-packs/_template/sample-sources.md` — sample candidate research
