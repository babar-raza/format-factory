---
artifact_id: TC-0006
artifact_type: taskcard
path: taskcards/TC-0006-release-manifest.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Builds release manifest generator. Resolves G-008, G-009, DEC-023.
---

# TC-0006: Release Manifest Generator

**Phase:** 3+
**Status:** not_started
**Owner:** TBD (developer)
**Created:** 2026-05-03
**Last updated:** 2026-05-03
**Blocking:** Gate 10 (automated release manifest); front matter validation at gates
**Blocked by:** Gate 9 (product mapping); TC-0005 (artifact index must exist)
**Format:** none (infrastructure)
**Gate:** none (enables Gate 10 and 11)

---

## Objective

Build the release manifest generator tool in `tools/` that: (1) validates artifact front matter across all committed artifacts, (2) generates a release manifest YAML listing all artifacts eligible for a given release type (OSS or commercial), and (3) verifies the commercial exclusion boundary. This resolves Gaps G-008 (visibility validation tooling) and G-009 (release manifest generator), and updates Decision DEC-023 to "Phase 3+: Implemented."

---

## Context

Phase 0 defined the artifact visibility schema in `docs/release-control.md` and noted that front matter validation tooling was deferred (DEC-023, TC-0006 scope). Until Gate 9, release manifests are created manually. Once FODS approaches Gate 10, the tool must exist to automate manifest generation and run the boundary check that the open-source release contains no commercial artifacts.

Gap G-008 requires front matter validation to be available at Gate 3 at the latest (samples need confirmed visibility). In practice, a lightweight validator should be available early in Phase 3 to catch front matter errors before Gate 7/8.

---

## Scope

### In scope

1. `tools/validation/validate_frontmatter.py` — Validates artifact front matter against the schema in `docs/release-control.md`. Must handle all committed artifact types.
2. `tools/validation/generate_manifest.py` — Generates a release manifest YAML from the artifact index, filtered by release type (oss | commercial).
3. `tools/validation/check_boundary.py` — Verifies that no commercial artifact appears in the OSS manifest and that no file in `src/python/{format}/` or `src/net/{format}/` (FOSS tiers) references any commercial namespace.
4. Integration with the artifact index (`tools/llm/artifact_index.py` from TC-0005).

### Out of scope

- Full CI pipeline (that is Phase 4+)
- Automatic publishing (that is Gate 10/11 work)
- Validating anything before TC-0005 artifact index exists

---

## Acceptance Criteria

- [ ] `tools/validation/validate_frontmatter.py` exists; runs against all committed artifacts; reports all front matter violations
- [ ] `tools/validation/generate_manifest.py` generates a valid release manifest for the OSS track
- [ ] `tools/validation/check_boundary.py` detects and reports any commercial namespace in the OSS source
- [ ] Front matter validation run against all Phase 0-3 artifacts with zero unresolved violations before Gate 10
- [ ] G-008 and G-009 marked resolved in `plans/master-plan.md`
- [ ] DEC-023 updated to "Phase 3+: Implemented"
- [ ] Self-challenge completed (AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Front matter validator | `tools/validation/validate_frontmatter.py` | internal | |
| Manifest generator | `tools/validation/generate_manifest.py` | internal | |
| Boundary checker | `tools/validation/check_boundary.py` | internal | |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Release control policy | `docs/release-control.md` | Required |
| Artifact index module | `tools/llm/artifact_index.py` | Required (TC-0005) |
| Format registry | `registry/format-registry.yaml` | Required |

---

## Steps

1. Read `docs/release-control.md` for the artifact visibility schema and eligibility rules.
2. Implement `validate_frontmatter.py`: scan all committed artifacts, parse front matter YAML, validate all required fields.
3. Implement `generate_manifest.py`: read artifact index, filter by `publish_allowed: true` and release type, output manifest YAML.
4. Implement `check_boundary.py`: scan `src/python/{format}/` and `src/net/{format}/` FOSS tiers for commercial namespace references; scan release manifest for `visibility: commercial` entries.
5. Run validation against all Phase 0 artifacts. Fix any front matter issues found.
6. Resolve gaps and decisions in `plans/master-plan.md`.
7. Complete self-challenge.

---

## Completion Record

**Completed by:** (to be filled)
**Completion date:** (to be filled)
**Artifacts produced:** (to be filled)
**Gaps discovered:** (to be filled)
**Notes:** (to be filled)
